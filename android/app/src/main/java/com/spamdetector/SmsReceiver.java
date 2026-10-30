package com.spamdetector;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.telephony.SmsMessage;
import android.util.Log;

/**
 * SmsReceiver
 * ───────────
 * BroadcastReceiver that fires automatically when an SMS arrives.
 * Extracts the sender number and message body, then passes them
 * to ApiClient which calls the Flask spam-detection API.
 * If spam is detected, NotificationHelper shows an alert.
 */
public class SmsReceiver extends BroadcastReceiver {

    private static final String TAG    = "SpamDetector_SMS";
    private static final String ACTION = "android.provider.Telephony.SMS_RECEIVED";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (!ACTION.equals(intent.getAction())) return;

        Bundle bundle = intent.getExtras();
        if (bundle == null) return;

        // ── Extract SMS messages from the bundle ──────────────────────────
        Object[] pdus    = (Object[]) bundle.get("pdus");
        String   format  = bundle.getString("format");
        if (pdus == null || pdus.length == 0) return;

        StringBuilder body   = new StringBuilder();
        String        sender = "";

        for (Object pdu : pdus) {
            SmsMessage sms = SmsMessage.createFromPdu((byte[]) pdu, format);
            if (sms == null) continue;
            sender = sms.getDisplayOriginatingAddress();
            body.append(sms.getMessageBody());
        }

        final String finalSender  = sender;
        final String finalMessage = body.toString().trim();

        if (finalMessage.isEmpty()) return;

        Log.d(TAG, "SMS received from: " + finalSender);
        Log.d(TAG, "Message: " + finalMessage);

        // ── Call Flask API in a background thread ─────────────────────────
        ApiClient.checkSpam(context, finalSender, finalMessage,
            new ApiClient.SpamCallback() {
                @Override
                public void onResult(boolean isSpam, String label,
                                     double confidence, String message) {
                    Log.d(TAG, "Result: " + label + " (" + confidence + "%)");

                    if (isSpam) {
                        // Show a spam warning notification
                        NotificationHelper.showSpamAlert(
                            context, finalSender, finalMessage,
                            confidence
                        );
                    } else {
                        // Optionally show a subtle "safe" notification
                        NotificationHelper.showSafeMessage(
                            context, finalSender, confidence
                        );
                    }
                }

                @Override
                public void onError(String error) {
                    Log.e(TAG, "API error: " + error);
                    // Show a fallback notification if API is unreachable
                    NotificationHelper.showApiError(context, finalSender);
                }
            }
        );
    }
}
