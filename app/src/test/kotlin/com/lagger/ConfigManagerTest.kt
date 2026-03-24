package com.lagger

import org.junit.Test
import org.junit.Assert.*

class ConfigManagerTest {
    @Test
    fun testParseConfig() {
        val json = "{\"name\": \"Test\", \"lag_ms\": 300, \"drop_rate\": 10, \"auto_off_ms\": 2000, \"mode\": \"toggle\"}"
        val config = ConfigManager.parseConfig(json)
        assertNotNull(config)
        assertEquals("Test", config?.name)
        assertEquals(300, config?.lagMs)
        assertEquals(10, config?.dropRate)
        assertEquals(2000, config?.autoOffMs)
        assertEquals("toggle", config?.mode)
    }

    @Test
    fun testParseInvalidConfig() {
        val json = "{\"invalid\": \"json\"}"
        val config = ConfigManager.parseConfig(json)
        assertNull(config)
    }
}
