package com.v2ray.ang.ui.onboarding

import android.app.Application
import androidx.lifecycle.viewModelScope
import com.v2ray.ang.AppConfig
import com.v2ray.ang.enums.Language
import com.v2ray.ang.enums.Region
import com.v2ray.ang.handler.MmkvManager
import com.v2ray.ang.handler.SettingsChangeManager
import com.v2ray.ang.handler.SettingsManager
import com.v2ray.ang.ui.base.BaseViewModel
import com.v2ray.ang.util.LogUtil
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.Locale

enum class OnboardingStep { Country, Language }

data class OnboardingUiState(
    val step: OnboardingStep = OnboardingStep.Country,
    val region: Region? = null,
    /** Language code from [Language]; null until the user reaches or picks on the language step. */
    val languageCode: String? = null,
    val isSaving: Boolean = false,
    /** Set once settings are saved; the activity then applies [languageCode] and closes. */
    val finishedLanguageCode: String? = null,
)

sealed interface OnboardingAction {
    data class SelectRegion(val region: Region) : OnboardingAction
    data class SelectLanguage(val code: String) : OnboardingAction
    data object Next : OnboardingAction
    data object Back : OnboardingAction
    data object Finish : OnboardingAction
}

class OnboardingViewModel(application: Application) : BaseViewModel(application) {

    private val _uiState = MutableStateFlow(OnboardingUiState())
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            val (savedRegion, savedLanguage) = withContext(Dispatchers.IO) {
                Region.fromCode(MmkvManager.decodeSettingsString(AppConfig.PREF_DRVPN_REGION)) to
                        MmkvManager.decodeSettingsString(AppConfig.PREF_LANGUAGE)
            }
            val region = savedRegion ?: regionFromDeviceLocale()
            val language = savedLanguage?.takeIf { it != Language.AUTO.code }
            _uiState.update { it.copy(region = it.region ?: region, languageCode = it.languageCode ?: language) }
        }
    }

    fun onAction(action: OnboardingAction) {
        when (action) {
            is OnboardingAction.SelectRegion -> _uiState.update { it.copy(region = action.region) }
            is OnboardingAction.SelectLanguage -> _uiState.update { it.copy(languageCode = action.code) }
            OnboardingAction.Next -> _uiState.update { state ->
                val region = state.region ?: return@update state
                state.copy(
                    step = OnboardingStep.Language,
                    languageCode = state.languageCode ?: region.suggestedLanguage.code,
                )
            }

            OnboardingAction.Back -> _uiState.update { it.copy(step = OnboardingStep.Country) }
            OnboardingAction.Finish -> finish()
        }
    }

    private fun finish() {
        val state = _uiState.value
        val region = state.region ?: return
        val languageCode = state.languageCode ?: region.suggestedLanguage.code
        if (state.isSaving) return
        _uiState.update { it.copy(isSaving = true) }
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                try {
                    val previous = MmkvManager.decodeSettingsString(AppConfig.PREF_DRVPN_REGION)
                    if (previous != region.code) {
                        // Only replace routing when the country changes, so custom rules survive a re-visit.
                        SettingsManager.resetRoutingRulesetsFromPresets(app, region.routingType)
                        MmkvManager.encodeSettings(AppConfig.PREF_DRVPN_REGION, region.code)
                        SettingsChangeManager.makeRestartService()
                    }
                } catch (e: Exception) {
                    LogUtil.e(AppConfig.TAG, "Onboarding: failed to apply routing for region ${region.code}", e)
                }
                MmkvManager.encodeSettings(AppConfig.PREF_DRVPN_ONBOARDING_DONE, true)
            }
            _uiState.update { it.copy(isSaving = false, finishedLanguageCode = languageCode) }
        }
    }

    private fun regionFromDeviceLocale(): Region? = when (Locale.getDefault().country.uppercase(Locale.ROOT)) {
        "IR" -> Region.IRAN
        "CN" -> Region.CHINA
        "RU" -> Region.RUSSIA
        else -> null
    }
}
