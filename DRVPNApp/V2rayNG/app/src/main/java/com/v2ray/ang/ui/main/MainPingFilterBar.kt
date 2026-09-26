package com.v2ray.ang.ui.main

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.selection.toggleable
import androidx.compose.material3.Checkbox
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import com.v2ray.ang.R

/**
 * Above the server list: a checkbox to also show servers without a ping result,
 * and a shortcut to ping every server (servers appear as they respond).
 */
@Composable
fun PingFilterBar(
    showServersWithoutPing: Boolean,
    isTesting: Boolean,
    onShowChange: (Boolean) -> Unit,
    onTestAll: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 4.dp, end = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Row(
            modifier = Modifier
                .weight(1f)
                .toggleable(
                    value = showServersWithoutPing,
                    role = Role.Checkbox,
                    onValueChange = onShowChange,
                )
                .padding(vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Checkbox(checked = showServersWithoutPing, onCheckedChange = null)
            Text(
                text = stringResource(R.string.ping_filter_show_all),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        TextButton(onClick = onTestAll, enabled = !isTesting) {
            Text(stringResource(R.string.ping_filter_test_all))
        }
    }
}
