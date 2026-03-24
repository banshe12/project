package com.lagger

import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.FrameLayout
import kotlinx.coroutines.*
import kotlin.math.abs

class OverlayService : Service() {

    private lateinit var windowManager: WindowManager
    private var overlayView: View? = null
    private lateinit var params: WindowManager.LayoutParams
    private var ledView: View? = null

    private var initialX: Int = 0
    private var initialY: Int = 0
    private var initialTouchX: Float = 0f
    private var initialTouchY: Float = 0f

    private var isActive = false
    private var config: Config = ConfigManager.getDefaultConfig()

    private val serviceScope = CoroutineScope(Dispatchers.Main + Job())
    private var autoOffJob: Job? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        NotificationHelper.createNotificationChannel(this)
        val notification = NotificationHelper.getNotification(this, "Lagger Overlay", "Overlay Active")
        startForeground(2, notification)

        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        setupOverlay()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val configJson = intent?.getStringExtra("config_json")
        if (configJson != null) {
            ConfigManager.parseConfig(configJson)?.let {
                config = it
            }
        }
        return super.onStartCommand(intent, flags, startId)
    }

    private fun setupOverlay() {
        val layoutType = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        )

        params.gravity = Gravity.TOP or Gravity.START
        params.x = 100
        params.y = 100

        overlayView = LayoutInflater.from(this).inflate(R.layout.overlay_status_led, null)
        ledView = overlayView?.findViewById(R.id.status_led)

        setupTouchListener()
        windowManager.addView(overlayView, params)
    }

    private fun setupTouchListener() {
        overlayView?.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    initialX = params.x
                    initialY = params.y
                    initialTouchX = event.rawX
                    initialTouchY = event.rawY
                    true
                }
                MotionEvent.ACTION_MOVE -> {
                    params.x = initialX + (event.rawX - initialTouchX).toInt()
                    params.y = initialY + (event.rawY - initialTouchY).toInt()
                    windowManager.updateViewLayout(overlayView, params)
                    true
                }
                MotionEvent.ACTION_UP -> {
                    val deltaX = abs(event.rawX - initialTouchX)
                    val deltaY = abs(event.rawY - initialTouchY)
                    if (deltaX < 10 && deltaY < 10) {
                        toggleLag()
                    }
                    true
                }
                else -> false
            }
        }
    }

    private fun toggleLag() {
        isActive = !isActive
        updateLedUI()
        notifyVpnService(isActive)

        if (isActive && config.autoOffMs > 0) {
            startAutoOffTimer()
        } else {
            autoOffJob?.cancel()
        }
    }

    private fun startAutoOffTimer() {
        autoOffJob?.cancel()
        autoOffJob = serviceScope.launch {
            delay(config.autoOffMs.toLong())
            if (isActive) {
                isActive = false
                updateLedUI()
                notifyVpnService(false)
            }
        }
    }

    private fun notifyVpnService(active: Boolean) {
        val intent = Intent(this, LaggerVpnService::class.java).apply {
            action = if (active) LaggerVpnService.ACTION_LAG_ON else LaggerVpnService.ACTION_LAG_OFF
        }
        startService(intent)
    }

    private fun updateLedUI() {
        ledView?.setBackgroundResource(
            if (isActive) R.drawable.led_active else R.drawable.led_idle
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
        overlayView?.let { windowManager.removeView(it) }
    }

    companion object {
        private const val TAG = "OverlayService"
    }
}
