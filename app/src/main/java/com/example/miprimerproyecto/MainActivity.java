package com.example.miprimerproyecto;

import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.View;

import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;

/**
 * Full-screen welcome screen for the first Android project.
 *
 * <p>The layout is deliberately small and responsive: the 9-patch supplies the artwork,
 * while ConstraintLayout positions the title and the button with bias values that have
 * orientation / smallest-width overrides in {@code res/values-*}.</p>
 */
public class MainActivity extends AppCompatActivity {

    private int initialPaddingLeft;
    private int initialPaddingTop;
    private int initialPaddingRight;
    private int initialPaddingBottom;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Draw the 9-patch edge-to-edge behind the status and navigation bars.
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        getWindow().setStatusBarColor(Color.TRANSPARENT);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            getWindow().setNavigationBarColor(Color.TRANSPARENT);
        } else {
            // Before Android 8.0 dark navigation icons are not available, so keep a dark bar.
            getWindow().setNavigationBarColor(Color.BLACK);
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            getWindow().setNavigationBarContrastEnforced(false);
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            getWindow().getAttributes().layoutInDisplayCutoutMode =
                    android.view.WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
        }

        setContentView(R.layout.activity_main);

        applyResponsiveBiases();
        configureSystemBarIcons();
        configureInsets();
        configureEnterButton();
    }

    /**
     * ConstraintLayout's XML parser only accepts a literal float for
     * layout_constraintVertical_bias, so the qualified fraction resources are applied here.
     * This keeps one layout for phones/tablets and portrait/landscape while still using
     * values-land / values-sw600dp overrides.
     */
    private void applyResponsiveBiases() {
        applyVerticalBias(R.id.welcome_title, R.fraction.title_vertical_bias);
        applyVerticalBias(R.id.enter_button, R.fraction.enter_vertical_bias);
    }

    private void applyVerticalBias(int viewId, int fractionResource) {
        View view = findViewById(viewId);
        ConstraintLayout.LayoutParams params = (ConstraintLayout.LayoutParams) view.getLayoutParams();
        params.verticalBias = getResources().getFraction(fractionResource, 1, 1);
        view.setLayoutParams(params);
    }

    private void configureSystemBarIcons() {
        WindowInsetsControllerCompat controller =
                WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView());
        // White status-bar icons over the blue sky.
        controller.setAppearanceLightStatusBars(false);
        // The bottom of the artwork is white, so dark navigation icons are readable.
        controller.setAppearanceLightNavigationBars(Build.VERSION.SDK_INT >= Build.VERSION_CODES.O);
    }

    private void configureInsets() {
        final View root = findViewById(R.id.root);
        initialPaddingLeft = root.getPaddingLeft();
        initialPaddingTop = root.getPaddingTop();
        initialPaddingRight = root.getPaddingRight();
        initialPaddingBottom = root.getPaddingBottom();

        ViewCompat.setOnApplyWindowInsetsListener(root, (view, windowInsets) -> {
            Insets bars = windowInsets.getInsets(
                    WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
            view.setPadding(
                    initialPaddingLeft + bars.left,
                    initialPaddingTop + bars.top,
                    initialPaddingRight + bars.right,
                    initialPaddingBottom + bars.bottom);
            return windowInsets;
        });
        ViewCompat.requestApplyInsets(root);
    }

    private void configureEnterButton() {
        findViewById(R.id.enter_button).setOnClickListener(view ->
                android.widget.Toast.makeText(
                        MainActivity.this,
                        R.string.entered_message,
                        android.widget.Toast.LENGTH_SHORT).show());
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            // Re-apply the icon colours after the system bars come back from a transient state.
            configureSystemBarIcons();
        }
    }
}
