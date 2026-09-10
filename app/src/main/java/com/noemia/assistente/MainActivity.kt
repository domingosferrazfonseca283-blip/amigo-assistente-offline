package com.noemia.assistente

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat

class MainActivity : ComponentActivity() {
    private val audioPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        setContent { NoemiaScreen(granted) }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val granted = ContextCompat.checkSelfPermission(
            this, Manifest.permission.RECORD_AUDIO
        ) == PackageManager.PERMISSION_GRANTED
        setContent { NoemiaScreen(granted) }
    }

    private fun requestAudio() = audioPermission.launch(Manifest.permission.RECORD_AUDIO)

    @Composable
    private fun NoemiaScreen(microphoneGranted: Boolean) {
        MaterialTheme {
            Column(
                modifier = Modifier.fillMaxSize().padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text("Noémia", style = MaterialTheme.typography.headlineLarge)
                Text(
                    text = if (microphoneGranted) "Estou pronta para ouvir você." else "Toque para ativar o microfone.",
                    modifier = Modifier.padding(top = 12.dp, bottom = 24.dp)
                )
                if (!microphoneGranted) {
                    Button(onClick = ::requestAudio) { Text("Ativar voz") }
                } else {
                    Button(onClick = { /* próxima etapa: reconhecimento offline */ }) {
                        Text("🎙️ Falar com Noémia")
                    }
                }
            }
        }
    }
}
