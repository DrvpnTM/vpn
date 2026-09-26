package com.v2ray.ang.enums

import androidx.annotation.StringRes
import com.v2ray.ang.R

/**
 * Country chosen on first launch. It picks the routing preset (sites of that country go direct)
 * and the suggested app language.
 */
enum class Region(
    val code: String,
    val flag: String,
    @StringRes val labelRes: Int,
    val routingType: RoutingType,
    val suggestedLanguage: Language,
) {
    IRAN("ir", "🇮🇷", R.string.region_iran, RoutingType.WHITE_IRAN, Language.PERSIAN),
    CHINA("cn", "🇨🇳", R.string.region_china, RoutingType.WHITE, Language.CHINA),
    RUSSIA("ru", "🇷🇺", R.string.region_russia, RoutingType.WHITE_RUSSIA, Language.RUSSIAN),
    OTHER("other", "🌐", R.string.region_other, RoutingType.GLOBAL, Language.ENGLISH);

    companion object {
        fun fromCode(code: String?): Region? = entries.find { it.code == code }
    }
}
