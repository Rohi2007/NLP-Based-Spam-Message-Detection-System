package com.spamdetector;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

/**
 * BootReceiver
 * ────────────
 * Ensures the app is ready to receive SMS after device reboot.
 * Android re-registers manifest receivers automatically, but this
 * receiver can be used to restart any foreground services if needed.
 */
public class BootReceiver extends BroadcastReceiver {

    private static final String TAG = "SpamDetector_Boot";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            Log.d(TAG, "Device rebooted — Spam Detector is active and watching SMS.");
            // SmsReceiver is registered in manifest so it auto-starts.
            // No extra action needed unless you have a foreground service.
        }
    }
}
