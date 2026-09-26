package com.v2ray.ang.ui.main

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.onClick
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.v2ray.ang.R

private val ConnectedColor = Color(0xFF2EB67D)
private val DisconnectedColor = Color(0xFF8A94A6)

/**
 * Hiddify-style home: active profile card, a large connect button and the selected server card.
 */
@Composable
fun MainHomeTab(
    profileName: String,
    selectedServerName: String,
    isRunning: Boolean,
    statusText: String,
    onAction: (MainAction) -> Unit,
    onOpenProxies: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        ProfileCard(
            profileName = profileName,
            onUpdate = { onAction(MainAction.UpdateSubscriptions) },
        )

        Spacer(Modifier.height(48.dp))

        ConnectButton(
            isRunning = isRunning,
            onToggle = { onAction(MainAction.ToggleService) },
        )

        Spacer(Modifier.height(20.dp))

        Text(
            text = stringResource(if (isRunning) R.string.home_connected else R.string.home_tap_to_connect),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = if (isRunning) ConnectedColor else MaterialTheme.colorScheme.onSurfaceVariant,
        )

        if (isRunning && statusText.isNotBlank()) {
            Spacer(Modifier.height(8.dp))
            Text(
                text = statusText,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                modifier = Modifier
                    .clip(RoundedCornerShape(12.dp))
                    .clickable(onClick = { onAction(MainAction.TestCurrentServer) })
                    .padding(horizontal = 12.dp, vertical = 6.dp),
            )
        }

        Spacer(Modifier.height(40.dp))

        ServerCard(
            serverName = selectedServerName,
            onClick = onOpenProxies,
        )
    }
}

@Composable
private fun ProfileCard(profileName: String, onUpdate: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerHigh),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(start = 20.dp, end = 8.dp, top = 12.dp, bottom = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                painter = painterResource(R.drawable.ic_subscriptions_24dp),
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
            )
            Spacer(Modifier.width(12.dp))
            Text(
                text = profileName.ifBlank { stringResource(R.string.app_name) },
                style = MaterialTheme.typography.titleMedium,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier.weight(1f),
            )
            IconButton(onClick = onUpdate) {
                Icon(
                    painter = painterResource(R.drawable.ic_refresh_24dp),
                    contentDescription = stringResource(R.string.title_sub_update),
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
private fun ConnectButton(isRunning: Boolean, onToggle: () -> Unit) {
    val color by animateColorAsState(
        targetValue = if (isRunning) ConnectedColor else DisconnectedColor,
        label = "connectColor",
    )
    val pulse = rememberInfiniteTransition(label = "connectPulse")
    val haloScale by pulse.animateFloat(
        initialValue = 1f,
        targetValue = if (isRunning) 1.12f else 1.04f,
        animationSpec = infiniteRepeatable(tween(durationMillis = 1400), RepeatMode.Reverse),
        label = "haloScale",
    )
    val actionLabel = stringResource(if (isRunning) R.string.acc_stop else R.string.acc_start)
    val stateLabel = stringResource(if (isRunning) R.string.home_connected else R.string.connection_not_connected)

    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier
            .size(220.dp)
            .clearAndSetSemantics {
                role = Role.Button
                contentDescription = actionLabel
                stateDescription = stateLabel
                onClick(label = actionLabel) { onToggle(); true }
            },
    ) {
        Box(
            modifier = Modifier
                .size(200.dp)
                .scale(haloScale)
                .clip(CircleShape)
                .background(color.copy(alpha = 0.15f)),
        )
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(160.dp)
                .clip(CircleShape)
                .background(color)
                .clickable(onClick = onToggle),
        ) {
            Icon(
                painter = painterResource(R.drawable.ic_power_24dp),
                contentDescription = null,
                tint = Color.White,
                modifier = Modifier.size(72.dp),
            )
        }
    }
}

@Composable
private fun ServerCard(serverName: String, onClick: () -> Unit) {
    val title = stringResource(R.string.home_current_server)
    val name = serverName.ifBlank { stringResource(R.string.home_no_server) }
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .semantics(mergeDescendants = true) {},
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerHigh),
        onClick = onClick,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp, vertical = 16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Icon(
                painter = painterResource(R.drawable.ic_proxies_24dp),
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = name,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            Icon(
                painter = painterResource(R.drawable.ic_chevron_right_24dp),
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}
