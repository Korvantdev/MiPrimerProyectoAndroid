package com.example.miprimerproyecto;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Rect;
import android.graphics.drawable.NinePatchDrawable;
import android.view.View;
import android.widget.TextView;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;
import org.robolectric.annotation.GraphicsMode;
import org.robolectric.shadows.ShadowToast;

import java.io.File;
import java.io.FileOutputStream;

/**
 * Unit/UI tests that run on the JVM with Robolectric.
 *
 * <p>The screenshot methods render the real view hierarchy, including the 9-patch,
 * at the same dp sizes used by the emulator/device previews.</p>
 */
@RunWith(RobolectricTestRunner.class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = 35)
public class MainActivityTest {

    private static final String[] SCREEN_QUALIFIERS = {
            "w360dp-h640dp-port-xxhdpi",
            "w640dp-h360dp-land-xxhdpi",
            "w600dp-h960dp-port-xhdpi",
            "w960dp-h600dp-land-xhdpi"
    };

    private MainActivity launch(String qualifiers) {
        RuntimeEnvironment.setQualifiers(qualifiers);
        return Robolectric.buildActivity(MainActivity.class).setup().get();
    }

    @Test
    public void defaultLocaleIsSpanishAndButtonWorks() {
        MainActivity activity = launch("es-rES-w360dp-h640dp-port-xxhdpi");
        assertEquals("Bienvenido", activity.getString(R.string.welcome));
        assertEquals("Entrar", activity.getString(R.string.enter));

        ShadowToast.reset();
        activity.findViewById(R.id.enter_button).performClick();
        assertEquals(activity.getString(R.string.entered_message), ShadowToast.getTextOfLatestToast());
    }

    @Test
    public void englishStrings() {
        MainActivity activity = launch("en-rUS-w360dp-h640dp-port-xxhdpi");
        assertEquals("Welcome", activity.getString(R.string.welcome));
        assertEquals("Enter", activity.getString(R.string.enter));

        ShadowToast.reset();
        activity.findViewById(R.id.enter_button).performClick();
        assertEquals(activity.getString(R.string.entered_message), ShadowToast.getTextOfLatestToast());
    }

    @Test
    public void frenchStrings() {
        MainActivity activity = launch("fr-rFR-w360dp-h640dp-port-xxhdpi");
        assertEquals("Bienvenue", activity.getString(R.string.welcome));
        assertEquals("Entrer", activity.getString(R.string.enter));

        ShadowToast.reset();
        activity.findViewById(R.id.enter_button).performClick();
        assertEquals(activity.getString(R.string.entered_message), ShadowToast.getTextOfLatestToast());
    }

    @Test
    public void germanStrings() {
        MainActivity activity = launch("de-rDE-w360dp-h640dp-port-xxhdpi");
        assertEquals("Willkommen", activity.getString(R.string.welcome));
        assertEquals("Betreten", activity.getString(R.string.enter));

        ShadowToast.reset();
        activity.findViewById(R.id.enter_button).performClick();
        assertEquals(activity.getString(R.string.entered_message), ShadowToast.getTextOfLatestToast());
    }

    @Test
    public void allScreensUseNinePatchAndDoNotOverlap() {
        for (String qualifiers : SCREEN_QUALIFIERS) {
            MainActivity activity = launch(qualifiers);
            View root = activity.findViewById(R.id.root);
            TextView title = activity.findViewById(R.id.welcome_title);
            TextView button = activity.findViewById(R.id.enter_button);

            int width = activity.getResources().getDisplayMetrics().widthPixels;
            int height = activity.getResources().getDisplayMetrics().heightPixels;
            layout(root, width, height);

            assertNotNull("Background must be a NinePatchDrawable for " + qualifiers, root.getBackground());
            assertTrue("Background must be a NinePatchDrawable for " + qualifiers,
                    root.getBackground() instanceof NinePatchDrawable);

            Rect titleRect = boundsInRoot(title, root);
            Rect buttonRect = boundsInRoot(button, root);
            assertTrue("Title must be above the button for " + qualifiers, titleRect.bottom < buttonRect.top);
            assertTrue("Button must have a 48dp touch target for " + qualifiers,
                    button.getHeight() >= dp(activity, 48));
            assertTrue("Title must be one line for " + qualifiers,
                    title.getLineCount() == 1 && title.getLayout().getEllipsisCount(0) == 0);
            assertTrue("Title stays inside the screen for " + qualifiers,
                    titleRect.left >= 0 && titleRect.right <= width);
            assertTrue("Button stays inside the screen for " + qualifiers,
                    buttonRect.left >= 0 && buttonRect.right <= width);
            assertFalse("Content must not be hidden under the top bar for " + qualifiers,
                    titleRect.top < 0);
        }
    }

    @Test
    public void renderDocumentationScreenshots() throws Exception {
        render("es", "es-rES-w360dp-h640dp-port-xxhdpi", "phone-portrait-es");
        render("en", "en-rUS-w360dp-h640dp-port-xxhdpi", "phone-portrait-en");
        render("fr", "fr-rFR-w360dp-h640dp-port-xxhdpi", "phone-portrait-fr");
        render("de", "de-rDE-w360dp-h640dp-port-xxhdpi", "phone-portrait-de");
        render("es", "es-rES-w640dp-h360dp-land-xxhdpi", "phone-landscape-es");
        render("es", "es-rES-w600dp-h960dp-port-xhdpi", "tablet-portrait-es");
        render("es", "es-rES-w960dp-h600dp-land-xhdpi", "tablet-landscape-es");
    }

    private void render(String locale, String qualifiers, String name) throws Exception {
        MainActivity activity = launch(qualifiers);
        View root = activity.findViewById(R.id.root);
        int width = activity.getResources().getDisplayMetrics().widthPixels;
        int height = activity.getResources().getDisplayMetrics().heightPixels;
        layout(root, width, height);

        Bitmap bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bitmap);
        root.draw(canvas);

        File outDir = new File(System.getProperty("screenshot.dir", "build/screenshots"));
        if (!outDir.exists() && !outDir.mkdirs()) {
            throw new IllegalStateException("Could not create " + outDir);
        }
        File out = new File(outDir, name + ".png");
        try (FileOutputStream stream = new FileOutputStream(out)) {
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream);
        }
        assertTrue("Screenshot was not written: " + out, out.isFile() && out.length() > 0);

        // Keep the locale parameter part of the output contract for future screenshot sets.
        assertEquals(locale, activity.getResources().getConfiguration().getLocales().get(0).getLanguage());
    }

    private static void layout(View root, int width, int height) {
        root.measure(
                View.MeasureSpec.makeMeasureSpec(width, View.MeasureSpec.EXACTLY),
                View.MeasureSpec.makeMeasureSpec(height, View.MeasureSpec.EXACTLY));
        root.layout(0, 0, width, height);
    }

    private static Rect boundsInRoot(View view, View root) {
        Rect rect = new Rect();
        view.getDrawingRect(rect);
        int[] viewLocation = new int[2];
        int[] rootLocation = new int[2];
        view.getLocationInWindow(viewLocation);
        root.getLocationInWindow(rootLocation);
        rect.offset(viewLocation[0] - rootLocation[0], viewLocation[1] - rootLocation[1]);
        return rect;
    }

    private static int dp(MainActivity activity, int value) {
        return Math.round(value * activity.getResources().getDisplayMetrics().density);
    }
}
