package com.spamdetector;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

/**
 * MainActivity
 * ────────────
 * Home screen of the Spam Detector app.
 *
 * Features:
 *  • Requests SMS + notification permissions on first launch
 *  • Shows whether SMS auto-detection is active
 *  • Lets user manually type/paste a message to test
 *  • Lets user configure the Flask server IP
 *  • Shows a live connection status indicator
 */
public class MainActivity extends AppCompatActivity {

    // Permission request codes
    private static final int REQ_SMS         = 101;
    private static final int REQ_NOTIF       = 102;

    // UI elements
    private TextView    tvStatus;
    private TextView    tvStatusDot;
    private EditText    etServerIp;
    private EditText    etTestMessage;
    private Button      btnSaveIp;
    private Button      btnPing;
    private Button      btnTestMessage;
    private ProgressBar progressBar;
    private LinearLayout resultCard;
    private ImageView   ivResultIcon;
    private TextView    tvResultLabel;
    private TextView    tvResultConfidence;
    private TextView    tvResultMessage;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Create notification channels
        NotificationHelper.createChannels(this);

        // Bind views
        bindViews();

        // Load saved server IP
        etServerIp.setText(ApiClient.getServerIp(this));

        // Request permissions
        requestPermissions();

        // Button listeners
        btnSaveIp.setOnClickListener(v -> saveServerIp());
        btnPing.setOnClickListener(v -> pingServer());
        btnTestMessage.setOnClickListener(v -> testMessage());
    }

    // ── Bind all UI views ─────────────────────────────────────────────────────
    private void bindViews() {
        tvStatus            = findViewById(R.id.tvStatus);
        tvStatusDot         = findViewById(R.id.tvStatusDot);
        etServerIp          = findViewById(R.id.etServerIp);
        etTestMessage       = findViewById(R.id.etTestMessage);
        btnSaveIp           = findViewById(R.id.btnSaveIp);
        btnPing             = findViewById(R.id.btnPing);
        btnTestMessage      = findViewById(R.id.btnTestMessage);
        progressBar         = findViewById(R.id.progressBar);
        resultCard          = findViewById(R.id.resultCard);
        ivResultIcon        = findViewById(R.id.ivResultIcon);
        tvResultLabel       = findViewById(R.id.tvResultLabel);
        tvResultConfidence  = findViewById(R.id.tvResultConfidence);
        tvResultMessage     = findViewById(R.id.tvResultMessage);
    }

    // ── Save server IP ────────────────────────────────────────────────────────
    private void saveServerIp() {
        String ip = etServerIp.getText().toString().trim();
        if (ip.isEmpty()) {
            Toast.makeText(this, "Enter a valid IP address", Toast.LENGTH_SHORT).show();
            return;
        }
        ApiClient.saveServerIp(this, ip);
        Toast.makeText(this, "Server IP saved: " + ip, Toast.LENGTH_SHORT).show();
        pingServer();
    }

    // ── Ping Flask server ─────────────────────────────────────────────────────
    private void pingServer() {
        tvStatus.setText("Checking connection…");
        tvStatusDot.setText("●");
        tvStatusDot.setTextColor(getColor(android.R.color.darker_gray));

        ApiClient.ping(this, isReachable -> {
            if (isReachable) {
                tvStatus.setText("Connected to Flask API ✓");
                tvStatusDot.setText("●");
                tvStatusDot.setTextColor(0xFF057A55);
                Toast.makeText(this, "Server is reachable!", Toast.LENGTH_SHORT).show();
            } else {
                tvStatus.setText("Cannot reach Flask API ✗");
                tvStatusDot.setText("●");
                tvStatusDot.setTextColor(0xFFE02424);
                Toast.makeText(this,
                    "Server unreachable. Check IP and make sure app.py is running.",
                    Toast.LENGTH_LONG).show();
            }
        });
    }

    // ── Manually test a message ───────────────────────────────────────────────
    private void testMessage() {
        String msg = etTestMessage.getText().toString().trim();
        if (msg.isEmpty()) {
            Toast.makeText(this, "Enter a message to test", Toast.LENGTH_SHORT).show();
            return;
        }

        progressBar.setVisibility(View.VISIBLE);
        resultCard.setVisibility(View.GONE);
        btnTestMessage.setEnabled(false);

        ApiClient.checkSpam(this, "Manual Test", msg, new ApiClient.SpamCallback() {
            @Override
            public void onResult(boolean isSpam, String label,
                                  double confidence, String message) {
                progressBar.setVisibility(View.GONE);
                btnTestMessage.setEnabled(true);
                showResult(isSpam, label, confidence, msg);
            }

            @Override
            public void onError(String error) {
                progressBar.setVisibility(View.GONE);
                btnTestMessage.setEnabled(true);
                Toast.makeText(MainActivity.this,
                    "Error: " + error + "\nMake sure Flask server is running.",
                    Toast.LENGTH_LONG).show();
            }
        });
    }

    // ── Render result card ────────────────────────────────────────────────────
    private void showResult(boolean isSpam, String label,
                             double confidence, String message) {
        resultCard.setVisibility(View.VISIBLE);

        if (isSpam) {
            resultCard.setBackgroundResource(R.drawable.bg_spam);
            ivResultIcon.setImageResource(android.R.drawable.ic_dialog_alert);
            tvResultLabel.setText("🚨 SPAM Detected");
            tvResultLabel.setTextColor(0xFFE02424);
        } else {
            resultCard.setBackgroundResource(R.drawable.bg_safe);
            ivResultIcon.setImageResource(android.R.drawable.ic_dialog_info);
            tvResultLabel.setText("✅ Legitimate Message");
            tvResultLabel.setTextColor(0xFF057A55);
        }

        tvResultConfidence.setText(String.format("Confidence: %.1f%%", confidence));
        tvResultMessage.setText(message.length() > 100
            ? message.substring(0, 100) + "…" : message);

        resultCard.animate().alpha(1f).setDuration(300).start();
    }

    // ── Request permissions ───────────────────────────────────────────────────
    private void requestPermissions() {
        // SMS permissions
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECEIVE_SMS)
                != PackageManager.PERMISSION_GRANTED ||
            ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS)
                != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(this,
                new String[]{
                    Manifest.permission.RECEIVE_SMS,
                    Manifest.permission.READ_SMS
                }, REQ_SMS);
        }

        // Notification permission (Android 13+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this,
                    Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.POST_NOTIFICATIONS},
                    REQ_NOTIF);
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode,
                                            @NonNull String[] permissions,
                                            @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (requestCode == REQ_SMS) {
            boolean granted = grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED;
            if (granted) {
                tvStatus.setText("SMS permission granted — auto-detection active ✓");
                Toast.makeText(this,
                    "SMS permission granted! Spam detection is now active.",
                    Toast.LENGTH_LONG).show();
            } else {
                tvStatus.setText("SMS permission denied — auto-detection disabled ✗");
                Toast.makeText(this,
                    "SMS permission denied. Auto-detection will not work.",
                    Toast.LENGTH_LONG).show();
            }
        }
    }
}
