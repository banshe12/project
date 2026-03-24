package com.lagger

import android.content.Intent
import android.net.VpnService
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private val VPN_REQUEST_CODE = 0
    private val OVERLAY_REQUEST_CODE = 1

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<Button>(R.id.btn_start_vpn).setOnClickListener {
            prepareVpn()
        }

        findViewById<Button>(R.id.btn_stop_all).setOnClickListener {
            stopAll()
        }
    }

    private fun prepareVpn() {
        val intent = VpnService.prepare(this)
        if (intent != null) {
            startActivityForResult(intent, VPN_REQUEST_CODE)
        } else {
            onActivityResult(VPN_REQUEST_CODE, RESULT_OK, null)
        }
    }

    private fun checkOverlayPermission(): Boolean {
        return if (Settings.canDrawOverlays(this)) {
            true
        } else {
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
            startActivityForResult(intent, OVERLAY_REQUEST_CODE)
            false
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == VPN_REQUEST_CODE && resultCode == RESULT_OK) {
            if (checkOverlayPermission()) {
                startServices()
            }
        } else if (requestCode == OVERLAY_REQUEST_CODE) {
            if (Settings.canDrawOverlays(this)) {
                startServices()
            } else {
                Toast.makeText(this, "Overlay permission required", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun startServices() {
        val config = ConfigManager.getDefaultConfig()
        val configJson = "{\"name\": \"${config.name}\", \"lag_ms\": ${config.lagMs}, \"drop_rate\": ${config.dropRate}, \"auto_off_ms\": ${config.autoOffMs}, \"mode\": \"${config.mode}\"}"

        val vpnIntent = Intent(this, LaggerVpnService::class.java).apply {
            putExtra("lag_ms", config.lagMs)
            putExtra("drop_rate", config.dropRate)
        }
        startService(vpnIntent)

        val overlayIntent = Intent(this, OverlayService::class.java).apply {
            putExtra("config_json", configJson)
        }
        startService(overlayIntent)

        Toast.makeText(this, "Services Started", Toast.LENGTH_SHORT).show()
    }

    private fun stopAll() {
        stopService(Intent(this, LaggerVpnService::class.java))
        stopService(Intent(this, OverlayService::class.java))
        Toast.makeText(this, "Services Stopped", Toast.LENGTH_SHORT).show()
    }
}
