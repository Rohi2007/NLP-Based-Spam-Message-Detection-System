package com.spamdetector;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * ApiClient
 * ─────────
 * Handles all HTTP communication with the Flask spam-detection API.
 * Runs network calls on a background thread and delivers results
 * back on the main thread via SpamCallback.
 *
 * API endpoint: POST http://<server_ip>:5000/predict
 * Request body: { "message": "...", "sender": "..." }
 * Response:     { "label": "spam|ham", "is_spam": true|false,
 *                 "confidence": 92.5, "cleaned": "..." }
 */
public class ApiClient {

    private static final String TAG             = "SpamDetector_API";
    private static final int    TIMEOUT_MS      = 8000;   // 8 seconds
    private static final String PREFS_NAME      = "SpamDetectorPrefs";
    private static final String PREF_SERVER_IP  = "server_ip";
    private static final String DEFAULT_IP      = "192.168.1.100"; // change in app settings

    // Single-thread executor so SMS checks run one at a time
    private static final ExecutorService executor = Executors.newSingleThreadExecutor();
    private static final Handler         mainHandler = new Handler(Looper.getMainLooper());

    // ── Callback interface ────────────────────────────────────────────────────
    public interface SpamCallback {
        void onResult(boolean isSpam, String label, double confidence, String message);
        void onError(String error);
    }

    // ── Get saved server IP from SharedPreferences ────────────────────────────
    public static String getServerIp(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        return prefs.getString(PREF_SERVER_IP, DEFAULT_IP);
    }

    // ── Save server IP to SharedPreferences ───────────────────────────────────
    public static void saveServerIp(Context context, String ip) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        prefs.edit().putString(PREF_SERVER_IP, ip.trim()).apply();
        Log.d(TAG, "Server IP saved: " + ip);
    }

    // ── Build full API URL ────────────────────────────────────────────────────
    private static String getApiUrl(Context context) {
        return "http://" + getServerIp(context) + ":5000/predict";
    }

    private static String getPingUrl(Context context) {
        return "http://" + getServerIp(context) + ":5000/ping";
    }

    // ── Check if message is spam ──────────────────────────────────────────────
    public static void checkSpam(Context context, String sender,
                                  String message, SpamCallback callback) {
        executor.execute(() -> {
            HttpURLConnection conn = null;
            try {
                // Build JSON body
                JSONObject body = new JSONObject();
                body.put("message", message);
                body.put("sender", sender);
                byte[] postData = body.toString().getBytes(StandardCharsets.UTF_8);

                // Open connection
                URL url = new URL(getApiUrl(context));
                conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json");
                conn.setRequestProperty("Accept", "application/json");
                conn.setConnectTimeout(TIMEOUT_MS);
                conn.setReadTimeout(TIMEOUT_MS);
                conn.setDoOutput(true);

                // Write body
                try (OutputStream os = conn.getOutputStream()) {
                    os.write(postData);
                }

                // Read response
                int responseCode = conn.getResponseCode();
                if (responseCode != HttpURLConnection.HTTP_OK) {
                    deliverError(callback, "Server error: HTTP " + responseCode);
                    return;
                }

                BufferedReader reader = new BufferedReader(
                    new InputStreamReader(conn.getInputStream(), StandardCharsets.UTF_8)
                );
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }
                reader.close();

                // Parse JSON response
                JSONObject json       = new JSONObject(response.toString());
                boolean    isSpam     = json.optBoolean("is_spam", false);
                String     label      = json.optString("label", "ham");
                double     confidence = json.optDouble("confidence", 50.0);
                String     cleaned    = json.optString("cleaned", "");

                Log.d(TAG, "API response → label=" + label + " confidence=" + confidence);

                // Deliver result on main thread
                mainHandler.post(() -> callback.onResult(isSpam, label, confidence, cleaned));

            } catch (Exception e) {
                Log.e(TAG, "API call failed: " + e.getMessage());
                deliverError(callback, e.getMessage());
            } finally {
                if (conn != null) conn.disconnect();
            }
        });
    }

    // ── Ping server to check connectivity ─────────────────────────────────────
    public static void ping(Context context, PingCallback callback) {
        executor.execute(() -> {
            HttpURLConnection conn = null;
            try {
                URL url = new URL(getPingUrl(context));
                conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("GET");
                conn.setConnectTimeout(4000);
                conn.setReadTimeout(4000);

                int code = conn.getResponseCode();
                boolean ok = (code == HttpURLConnection.HTTP_OK);
                mainHandler.post(() -> callback.onResult(ok));

            } catch (Exception e) {
                mainHandler.post(() -> callback.onResult(false));
            } finally {
                if (conn != null) conn.disconnect();
            }
        });
    }

    private static void deliverError(SpamCallback callback, String error) {
        mainHandler.post(() -> callback.onError(error));
    }

    // ── Ping callback ─────────────────────────────────────────────────────────
    public interface PingCallback {
        void onResult(boolean isReachable);
    }
}
