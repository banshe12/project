#!/bin/bash

# Create the Android Project
mkdir -p LaggerVpn/app/src/main/kotlin/com/lagger
mkdir -p LaggerVpn/app/src/main/res/layout
mkdir -p LaggerVpn/app/src/main/res/drawable
mkdir -p LaggerVpn/app/src/main/res/values
mkdir -p LaggerVpn/app/src/main/res/xml

cd LaggerVpn

# Root build file
cat <<EOF > build.gradle.kts
plugins {
    id("com.android.application") version "8.2.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
}
EOF

# Settings file
cat <<EOF > settings.gradle.kts
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "LaggerVpn"
include(":app")
EOF

# App build file
cat <<EOF > app/build.gradle.kts
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "com.lagger"
    compileSdk = 34
    defaultConfig {
        applicationId = "com.lagger"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions { jvmTarget = "1.8" }
}
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.cardview:cardview:1.0.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    testImplementation("junit:junit:4.13.2")
}
EOF

# Manifest
cat <<EOF > app/src/main/AndroidManifest.xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" xmlns:tools="http://schemas.android.com/tools">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.BIND_VPN_SERVICE" tools:ignore="ProtectedPermissions" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <application android:allowBackup="true" android:icon="@mipmap/ic_launcher" android:label="LaggerVpn" android:supportsRtl="true" android:theme="@style/Theme.LaggerVpn">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <service android:name=".LaggerVpnService" android:permission="android.permission.BIND_VPN_SERVICE" android:exported="false">
            <intent-filter><action android:name="android.net.VpnService" /></intent-filter>
        </service>
        <service android:name=".OverlayService" android:exported="false" android:foregroundServiceType="specialUse">
            <property android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE" android:value="Network manipulation for testing" />
        </service>
    </application>
</manifest>
EOF

# ConfigManager.kt
cat <<EOF > app/src/main/kotlin/com/lagger/ConfigManager.kt
package com.lagger
import org.json.JSONObject
data class Config(val name: String, val lagMs: Int, val dropRate: Int, val autoOffMs: Int, val mode: String)
object ConfigManager {
    fun parseConfig(jsonString: String): Config? {
        return try {
            val jsonObject = JSONObject(jsonString)
            Config(jsonObject.getString("name"), jsonObject.getInt("lag_ms"), jsonObject.getInt("drop_rate"), jsonObject.getInt("auto_off_ms"), jsonObject.getString("mode"))
        } catch (e: Exception) { null }
    }
    fun getDefaultConfig() = Config("Default", 500, 0, 5000, "toggle")
}
EOF

# NotificationHelper.kt
cat <<EOF > app/src/main/kotlin/com/lagger/NotificationHelper.kt
package com.lagger
import android.app.*
import android.content.Context
import android.os.Build
import androidx.core.app.NotificationCompat
object NotificationHelper {
    private const val CHANNEL_ID = "LaggerChannel"
    fun createNotificationChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(CHANNEL_ID, "Lagger VPN", NotificationManager.IMPORTANCE_LOW)
            (context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).createNotificationChannel(channel)
        }
    }
    fun getNotification(context: Context, title: String, msg: String): Notification {
        return NotificationCompat.Builder(context, CHANNEL_ID).setContentTitle(title).setContentText(msg).setSmallIcon(android.R.drawable.ic_dialog_info).build()
    }
}
EOF

# LaggerVpnService.kt
cat <<EOF > app/src/main/kotlin/com/lagger/LaggerVpnService.kt
package com.lagger
import android.content.Intent
import android.net.VpnService
import android.os.ParcelFileDescriptor
import android.util.Log
import java.io.*
import java.util.concurrent.*
import java.util.*
class LaggerVpnService : VpnService() {
    private var vpnInterface: ParcelFileDescriptor? = null
    private var isRunning = false
    private val random = Random()
    private var lagMs = 500
    private var dropRate = 0
    @Volatile private var isLagEnabled = false
    private val packetQueue = ConcurrentLinkedQueue<DelayedPacket>()
    private val executor = Executors.newFixedThreadPool(2)
    class DelayedPacket(val data: ByteArray, var sendAt: Long)
    override fun onCreate() { super.onCreate(); NotificationHelper.createNotificationChannel(this) }
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> stopVpn()
            ACTION_LAG_ON -> isLagEnabled = true
            ACTION_LAG_OFF -> { isLagEnabled = false; flushPackets() }
        }
        lagMs = intent?.getIntExtra("lag_ms", lagMs) ?: lagMs
        dropRate = intent?.getIntExtra("drop_rate", dropRate) ?: dropRate
        if (!isRunning) startVpn()
        return START_STICKY
    }
    private fun startVpn() {
        startForeground(1, NotificationHelper.getNotification(this, "LAGGER VPN", "CORE ACTIVE"))
        try {
            vpnInterface = Builder().setSession("LaggerVpn").addAddress("10.0.0.2", 32).addRoute("0.0.0.0", 0).establish()
            isRunning = true
            executor.execute { runLoop({ FileInputStream(it) }, { data -> handlePacket(data) }) }
            executor.execute { runWriter() }
        } catch (e: Exception) { stopVpn() }
    }
    private fun runLoop(streamProvider: (FileDescriptor) -> FileInputStream, handler: (ByteArray) -> Unit) {
        val input = streamProvider(vpnInterface!!.fileDescriptor)
        val buffer = ByteArray(16384)
        while (isRunning) {
            val len = input.read(buffer)
            if (len > 0) handler(buffer.copyOf(len))
        }
    }
    private fun handlePacket(data: ByteArray) {
        if (isLagEnabled && random.nextInt(100) < dropRate) return
        packetQueue.add(DelayedPacket(data, System.currentTimeMillis() + (if (isLagEnabled) lagMs else 0)))
    }
    private fun runWriter() {
        val output = FileOutputStream(vpnInterface!!.fileDescriptor)
        while (isRunning) {
            val now = System.currentTimeMillis()
            while (true) {
                val p = packetQueue.peek() ?: break
                if (p.sendAt <= now) { output.write(p.data); packetQueue.poll() } else break
            }
            Thread.sleep(1)
        }
    }
    private fun stopVpn() { isRunning = false; vpnInterface?.close(); stopSelf() }
    private fun flushPackets() { val now = System.currentTimeMillis(); packetQueue.forEach { it.sendAt = now } }
    companion object {
        const val ACTION_STOP = "com.lagger.STOP"; const val ACTION_LAG_ON = "com.lagger.ON"; const val ACTION_LAG_OFF = "com.lagger.OFF"
    }
}
EOF

# OverlayService.kt
cat <<EOF > app/src/main/kotlin/com/lagger/OverlayService.kt
package com.lagger
import android.app.Service
import android.content.*
import android.graphics.PixelFormat
import android.os.*
import android.view.*
import kotlinx.coroutines.*
import kotlin.math.abs
class OverlayService : Service() {
    private lateinit var windowManager: WindowManager
    private var overlayView: View? = null
    private var isActive = false
    private var config = ConfigManager.getDefaultConfig()
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    private var autoOffJob: Job? = null
    override fun onBind(intent: Intent?) = null
    override fun onCreate() {
        super.onCreate()
        NotificationHelper.createNotificationChannel(this)
        startForeground(2, NotificationHelper.getNotification(this, "LAGGER OVERLAY", "ACTIVE"))
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        setupOverlay()
    }
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        intent?.getStringExtra("config_json")?.let { ConfigManager.parseConfig(it)?.let { c -> config = c } }
        return super.onStartCommand(intent, flags, startId)
    }
    private fun setupOverlay() {
        val params = WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.TRANSLUCENT)
        overlayView = LayoutInflater.from(this).inflate(R.layout.overlay_status_led, null)
        overlayView?.setOnTouchListener(object : View.OnTouchListener {
            private var lastX = 0; private var lastY = 0; private var touchX = 0f; private var touchY = 0f
            override fun onTouch(v: View, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> { lastX = params.x; lastY = params.y; touchX = event.rawX; touchY = event.rawY }
                    MotionEvent.ACTION_MOVE -> { params.x = lastX + (event.rawX - touchX).toInt(); params.y = lastY + (event.rawY - touchY).toInt(); windowManager.updateViewLayout(overlayView, params) }
                    MotionEvent.ACTION_UP -> if (abs(event.rawX - touchX) < 10) toggle()
                }
                return true
            }
        })
        windowManager.addView(overlayView, params)
    }
    private fun toggle() {
        isActive = !isActive
        overlayView?.findViewById<View>(R.id.status_led)?.setBackgroundResource(if (isActive) R.drawable.led_active else R.drawable.led_idle)
        startService(Intent(this, LaggerVpnService::class.java).apply { action = if (isActive) LaggerVpnService.ACTION_LAG_ON else LaggerVpnService.ACTION_LAG_OFF })
        if (isActive && config.autoOffMs > 0) {
            autoOffJob?.cancel(); autoOffJob = scope.launch { delay(config.autoOffMs.toLong()); if (isActive) toggle() }
        }
    }
    override fun onDestroy() { super.onDestroy(); scope.cancel(); windowManager.removeView(overlayView) }
}
EOF

# MainActivity.kt
cat <<EOF > app/src/main/kotlin/com/lagger/MainActivity.kt
package com.lagger
import android.content.Intent
import android.net.VpnService
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        findViewById<Button>(R.id.btn_start_vpn).setOnClickListener {
            val intent = VpnService.prepare(this)
            if (intent != null) startActivityForResult(intent, 0) else startServices()
        }
        findViewById<Button>(R.id.btn_stop_all).setOnClickListener {
            stopService(Intent(this, LaggerVpnService::class.java))
            stopService(Intent(this, OverlayService::class.java))
        }
    }
    private fun startServices() {
        if (!Settings.canDrawOverlays(this)) { startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)); return }
        startService(Intent(this, LaggerVpnService::class.java))
        startService(Intent(this, OverlayService::class.java))
    }
    override fun onActivityResult(req: Int, res: Int, data: Intent?) { if (res == RESULT_OK) startServices() }
}
EOF

# Resources
cat <<EOF > app/src/main/res/values/colors.xml
<resources>
    <color name="black">#000000</color>
    <color name="neon_green">#39FF14</color>
    <color name="neon_red">#FF3131</color>
</resources>
EOF

cat <<EOF > app/src/main/res/values/themes.xml
<resources>
    <style name="Theme.LaggerVpn" parent="Theme.Material3.DayNight.NoActionBar"></style>
</resources>
EOF

cat <<EOF > app/src/main/res/layout/activity_main.xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android" android:layout_width="match_parent" android:layout_height="match_parent" android:orientation="vertical" android:gravity="center" android:background="@color/black" android:padding="24dp">
    <Button android:id="@+id/btn_start_vpn" android:layout_width="match_parent" android:layout_height="60dp" android:text="ACTIVATE CORE" android:backgroundTint="@color/neon_green" android:textColor="@color/black" />
    <Button android:id="@+id/btn_stop_all" android:layout_width="match_parent" android:layout_height="60dp" android:text="TERMINATE" android:backgroundTint="@color/neon_red" android:textColor="@color/black" android:layout_marginTop="16dp" />
</LinearLayout>
EOF

cat <<EOF > app/src/main/res/layout/overlay_status_led.xml
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android" android:layout_width="wrap_content" android:layout_height="wrap_content">
    <View android:id="@+id/status_led" android:layout_width="40dp" android:layout_height="40dp" android:background="@drawable/led_idle" />
</FrameLayout>
EOF

cat <<EOF > app/src/main/res/drawable/led_idle.xml
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval"><solid android:color="#808080" /></shape>
EOF

cat <<EOF > app/src/main/res/drawable/led_active.xml
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval"><solid android:color="#39FF14" /></shape>
EOF

# Build Script logic
echo "Installing Android SDK..."
sudo apt-get update && sudo apt-get install -y openjdk-17-jdk wget unzip
mkdir -p $HOME/android-sdk/cmdline-tools
wget https://dl.google.com/android/repository/commandlinetools-linux-10406996_latest.zip -O cmdline-tools.zip
unzip cmdline-tools.zip -d $HOME/android-sdk/cmdline-tools
mv $HOME/android-sdk/cmdline-tools/cmdline-tools $HOME/android-sdk/cmdline-tools/latest
export ANDROID_HOME=$HOME/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
echo "yes" | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

chmod +x gradlew
./gradlew assembleRelease
echo "Build complete! APK path: \$(find . -name "*.apk" | grep release)"
