package com.v2ray.ang.ui.onboarding

import androidx.activity.compose.BackHandler
import androidx.activity.viewModels
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringArrayResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.v2ray.ang.R
import com.v2ray.ang.enums.Language
import com.v2ray.ang.enums.Region
import com.v2ray.ang.handler.AppLocaleManager
import com.v2ray.ang.ui.base.BaseComponentActivity

/**
 * First-run setup: pick a country (routing preset), then the app language.
 * Also reachable later from the main drawer.
 */
class OnboardingActivity : BaseComponentActivity() {

    private val viewModel: OnboardingViewModel by viewModels()

    @Composable
    override fun ScreenContent() {
        val uiState by viewModel.uiState.collectAsStateWithLifecycle()

        LaunchedEffect(uiState.finishedLanguageCode) {
            val code = uiState.finishedLanguageCode ?: return@LaunchedEffect
            setResult(RESULT_OK)
            finish()
            // Applied after finish(): AppCompat recreates the activities below with the new locale.
            AppLocaleManager.setApplicationLanguage(code)
        }

        BackHandler(enabled = uiState.step == OnboardingStep.Language) {
            viewModel.onAction(OnboardingAction.Back)
        }

        OnboardingScreen(state = uiState, onAction = viewModel::onAction)
    }
}

@Composable
private fun OnboardingScreen(state: OnboardingUiState, onAction: (OnboardingAction) -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .statusBarsPadding()
            .navigationBarsPadding()
            .padding(horizontal = 20.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.height(32.dp))
        Image(
            painter = painterResource(R.mipmap.ic_launcher_round),
            contentDescription = null,
            modifier = Modifier.size(88.dp),
        )
        Spacer(Modifier.height(12.dp))
        Text(
            text = stringResource(R.string.app_name),
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
        )
        Spacer(Modifier.height(24.dp))
        Text(
            text = stringResource(
                if (state.step == OnboardingStep.Country) R.string.onboarding_select_country
                else R.string.onboarding_select_language
            ),
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center,
        )
        if (state.step == OnboardingStep.Country) {
            Spacer(Modifier.height(4.dp))
            Text(
                text = stringResource(R.string.onboarding_country_hint),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
        }
        Spacer(Modifier.height(16.dp))

        when (state.step) {
            OnboardingStep.Country -> CountryList(
                selected = state.region,
                onSelect = { onAction(OnboardingAction.SelectRegion(it)) },
                modifier = Modifier.weight(1f),
            )

            OnboardingStep.Language -> LanguageList(
                selectedCode = state.languageCode,
                onSelect = { onAction(OnboardingAction.SelectLanguage(it)) },
                modifier = Modifier.weight(1f),
            )
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            if (state.step == OnboardingStep.Language) {
                TextButton(onClick = { onAction(OnboardingAction.Back) }) {
                    Text(stringResource(R.string.onboarding_back))
                }
            }
            Spacer(Modifier.weight(1f))
            Button(
                onClick = {
                    onAction(
                        if (state.step == OnboardingStep.Country) OnboardingAction.Next
                        else OnboardingAction.Finish
                    )
                },
                enabled = !state.isSaving && when (state.step) {
                    OnboardingStep.Country -> state.region != null
                    OnboardingStep.Language -> state.languageCode != null
                },
                contentPadding = PaddingValues(horizontal = 32.dp, vertical = 12.dp),
            ) {
                Text(
                    stringResource(
                        if (state.step == OnboardingStep.Country) R.string.onboarding_next
                        else R.string.onboarding_start
                    )
                )
            }
        }
    }
}

@Composable
private fun CountryList(selected: Region?, onSelect: (Region) -> Unit, modifier: Modifier = Modifier) {
    LazyColumn(modifier = modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        items(Region.entries, key = { it.code }) { region ->
            OptionRow(
                leading = region.flag,
                label = stringResource(region.labelRes),
                selected = region == selected,
                onClick = { onSelect(region) },
            )
        }
    }
}

@Composable
private fun LanguageList(selectedCode: String?, onSelect: (String) -> Unit, modifier: Modifier = Modifier) {
    val names = stringArrayResource(R.array.language_select)
    val codes = stringArrayResource(R.array.language_select_value)
    val options = codes.zip(names).filter { (code, _) -> code != Language.AUTO.code }
    LazyColumn(modifier = modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        items(options, key = { it.first }) { (code, name) ->
            OptionRow(
                leading = null,
                label = name,
                selected = code == selectedCode,
                onClick = { onSelect(code) },
            )
        }
    }
}

@Composable
private fun OptionRow(leading: String?, label: String, selected: Boolean, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .selectable(selected = selected, onClick = onClick, role = Role.RadioButton),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (selected) MaterialTheme.colorScheme.primaryContainer
            else MaterialTheme.colorScheme.surfaceContainerHigh
        ),
        border = if (selected) BorderStroke(2.dp, MaterialTheme.colorScheme.primary) else null,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 14.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            if (leading != null) {
                Text(text = leading, fontSize = 26.sp)
            }
            Text(
                text = label,
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.weight(1f),
            )
            RadioButton(selected = selected, onClick = null)
        }
    }
}
