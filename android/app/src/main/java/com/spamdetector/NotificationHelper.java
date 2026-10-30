package com.spamdetector;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;

/**
 * NotificationHelper
 * ──────────────────
 * Builds and displays notifications for spam alerts,
 * safe messages, and API connection errors.
 *
 * Channels:
 *   SPAM_CHANNEL   – high priority, shown as heads-up popup
 *   SAFE_CHANNEL   – low priority, silent
 *   ERROR_CHANNEL  – default priority
 */
public class NotificationHelper {

    // Notification channel IDs
    public static final String SPAM_CHANNEL  = "spam_alert_channel";
    public static final String SAFE_CHANNEL  = "safe_message_channel";
    public static final String ERROR_CHANNEL = "error_channel";

    // Unique notification IDs (use timestamp-based for multiple)
    private static int notifId = 1000;

    // ── Create all channels (call once at app start) ───────────────────────
    public static void createChannels(Context context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm =
                context.getSystemService(NotificationManager.class);

            // Spam channel — high importance (shows as heads-up popup)
            NotificationChannel spamChannel = new NotificationChannel(
                SPAM_CHANNEL,
                "Spam Alerts",
                NotificationManager.IMPORTANCE_HIGH
            );
            spamChannel.setDescription("Alerts for detected spam messages");
            spamChannel.enableVibration(true);
            spamChannel.setVibrationPattern(new long[]{0, 300, 200, 300});
            nm.createNotificationChannel(spamChannel);

            // Safe channel — low importance (silent, no popup)
            NotificationChannel safeChannel = new NotificationChannel(
                SAFE_CHANNEL,
                "Safe Messages",
                NotificationManager.IMPORTANCE_LOW
            );
            safeChannel.setDescription("Confirmation that a message is legitimate");
            nm.createNotificationChannel(safeChannel);

            // Error channel — default importance
            NotificationChannel errorChannel = new NotificationChannel(
                ERROR_CHANNEL,
                "Connection Errors",
                NotificationManager.IMPORTANCE_DEFAULT
            );
            errorChannel.setDescription("API connection error notifications");
            nm.createNotificationChannel(errorChannel);
        }
    }

    // ── Show SPAM alert notification ──────────────────────────────────────────
    public static void showSpamAlert(Context context, String sender,
                                      String message, double confidence) {
        Intent intent = new Intent(context, MainActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        PendingIntent pi = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        // Truncate message for display
        String preview = message.length() > 80
            ? message.substring(0, 80) + "…"
            : message;

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, SPAM_CHANNEL)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle("🚨 SPAM Detected!")
            .setContentText("From: " + sender)
            .setStyle(new NotificationCompat.BigTextStyle()
                .bigText("From: " + sender + "\n\n\"" + preview + "\"\n\n"
                    + "Confidence: " + String.format("%.1f", confidence) + "%"))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_MESSAGE)
            .setContentIntent(pi)
            .setAutoCancel(true)
            .setVibrate(new long[]{0, 300, 200, 300})
            .setColor(0xFFE02424);  // Red color

        NotificationManagerCompat.from(context)
            .notify(notifId++, builder.build());
    }

    // ── Show safe message notification ────────────────────────────────────────
    public static void showSafeMessage(Context context, String sender,
                                        double confidence) {
        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, SAFE_CHANNEL)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("✅ Legitimate Message")
            .setContentText("From " + sender + " — looks safe ("
                + String.format("%.1f", confidence) + "% confident)")
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setAutoCancel(true)
            .setColor(0xFF057A55);  // Green color

        NotificationManagerCompat.from(context)
            .notify(notifId++, builder.build());
    }

    // ── Show API error notification ───────────────────────────────────────────
    public static void showApiError(Context context, String sender) {
        Intent intent = new Intent(context, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, ERROR_CHANNEL)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle("⚠️ Spam Detector — API Unreachable")
            .setContentText("Could not check SMS from " + sender
                + ". Make sure Flask server is running.")
            .setStyle(new NotificationCompat.BigTextStyle()
                .bigText("Could not check SMS from " + sender + ".\n\n"
                    + "Make sure:\n"
                    + "• Flask server is running (python app.py)\n"
                    + "• Phone and PC are on the same WiFi\n"
                    + "• Server IP is correct in app settings"))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pi)
            .setAutoCancel(true);

        NotificationManagerCompat.from(context)
            .notify(notifId++, builder.build());
    }
}
