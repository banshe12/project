package com.lagger

import android.content.Intent
import android.net.VpnService
import android.os.ParcelFileDescriptor
import android.util.Log
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.IOException
import java.nio.ByteBuffer
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.Executors
import java.util.Random

/**
 * LaggerVpnService intercepts network traffic and simulates network delay/loss.
 *
 * NOTE: For full functionality where traffic is forwarded to the internet,
 * a user-space TCP/IP stack (like lwIP) or a transparent proxy is required.
 * This implementation demonstrates the core packet queue and delay logic
 * using the Android VpnService TUN interface.
 */
class LaggerVpnService : VpnService() {

    private var vpnInterface: ParcelFileDescriptor? = null
    private var isRunning = false
    private val random = Random()

    // Config values
    private var lagMs: Int = 0
    private var dropRate: Int = 0
    @Volatile private var isLagEnabled = false

    private val packetQueue = ConcurrentLinkedQueue<DelayedPacket>()
    private val executor = Executors.newFixedThreadPool(2)

    class DelayedPacket(val data: ByteArray, var sendAt: Long)

    override fun onCreate() {
        super.onCreate()
        NotificationHelper.createNotificationChannel(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action
        when (action) {
            ACTION_STOP -> {
                stopVpn()
                return START_NOT_STICKY
            }
            ACTION_LAG_ON -> {
                isLagEnabled = true
                Log.d(TAG, "Lag protocol activated")
            }
            ACTION_LAG_OFF -> {
                isLagEnabled = false
                flushPackets()
                Log.d(TAG, "Lag protocol deactivated - flushing packets")
            }
        }

        lagMs = intent?.getIntExtra("lag_ms", 500) ?: lagMs
        dropRate = intent?.getIntExtra("drop_rate", 0) ?: dropRate

        if (!isRunning) {
            startVpn()
        }
        return START_STICKY
    }

    private fun startVpn() {
        if (isRunning) return

        val notification = NotificationHelper.getNotification(this, "LAGGER VPN", "CORE ACTIVE")
        startForeground(1, notification)

        try {
            val builder = Builder()
            builder.setSession("LaggerVpn")
            builder.addAddress("10.0.0.2", 32)
            builder.addRoute("0.0.0.0", 0)
            builder.setMtu(1500)

            vpnInterface = builder.establish()
            if (vpnInterface != null) {
                isRunning = true
                Log.i(TAG, "VPN Interface established")

                executor.execute { runReader() }
                executor.execute { runWriter() }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error starting VPN", e)
            stopVpn()
        }
    }

    private fun runReader() {
        val input = FileInputStream(vpnInterface?.fileDescriptor)
        val buffer = ByteArray(16384)

        try {
            while (isRunning) {
                val length = input.read(buffer)
                if (length > 0) {
                    val packetData = buffer.copyOf(length)
                    handlePacket(packetData)
                }
            }
        } catch (e: IOException) {
            Log.e(TAG, "Reader loop failed", e)
        }
    }

    private fun handlePacket(packetData: ByteArray) {
        if (isLagEnabled) {
            if (random.nextInt(100) < dropRate) {
                return
            }
            packetQueue.add(DelayedPacket(packetData, System.currentTimeMillis() + lagMs))
        } else {
            packetQueue.add(DelayedPacket(packetData, System.currentTimeMillis()))
        }
    }

    private fun runWriter() {
        val output = FileOutputStream(vpnInterface?.fileDescriptor)

        try {
            while (isRunning) {
                val currentTime = System.currentTimeMillis()
                while (true) {
                    val delayedPacket = packetQueue.peek() ?: break
                    if (delayedPacket.sendAt <= currentTime) {
                        try {
                            output.write(delayedPacket.data)
                            packetQueue.poll()
                        } catch (e: IOException) {
                            Log.e(TAG, "Writer loop failed to write", e)
                            packetQueue.poll()
                        }
                    } else {
                        break
                    }
                }
                Thread.sleep(1)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Writer loop failed", e)
        }
    }

    private fun stopVpn() {
        isRunning = false
        try {
            vpnInterface?.close()
        } catch (e: IOException) {
            Log.e(TAG, "Error closing VPN interface", e)
        }
        vpnInterface = null
        stopSelf()
    }

    override fun onDestroy() {
        stopVpn()
        executor.shutdownNow()
        super.onDestroy()
    }

    private fun flushPackets() {
        val currentTime = System.currentTimeMillis()
        val iterator = packetQueue.iterator()
        while (iterator.hasNext()) {
            val delayedPacket = iterator.next()
            delayedPacket.sendAt = currentTime
        }
    }

    companion object {
        private const val TAG = "LaggerVpnService"
        const val ACTION_STOP = "com.lagger.STOP_VPN"
        const val ACTION_LAG_ON = "com.lagger.ACTION_LAG_ON"
        const val ACTION_LAG_OFF = "com.lagger.ACTION_LAG_OFF"
    }
}
