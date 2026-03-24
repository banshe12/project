package com.lagger

import org.json.JSONObject

data class Config(
    val name: String,
    val lagMs: Int,
    val dropRate: Int,
    val autoOffMs: Int,
    val mode: String
)

object ConfigManager {
    fun parseConfig(jsonString: String): Config? {
        return try {
            val jsonObject = JSONObject(jsonString)
            Config(
                name = jsonObject.getString("name"),
                lagMs = jsonObject.getInt("lag_ms"),
                dropRate = jsonObject.getInt("drop_rate"),
                autoOffMs = jsonObject.getInt("auto_off_ms"),
                mode = jsonObject.getString("mode")
            )
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    fun getDefaultConfig(): Config {
        return Config(
            name = "Default",
            lagMs = 500,
            dropRate = 0,
            autoOffMs = 5000,
            mode = "hold"
        )
    }
}
