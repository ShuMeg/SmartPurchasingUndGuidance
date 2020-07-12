package com.example.spug;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Toast;

import com.budiyev.android.codescanner.CodeScanner;
import com.budiyev.android.codescanner.CodeScannerView;
import com.budiyev.android.codescanner.DecodeCallback;
import com.google.zxing.Result;

import org.json.JSONException;
import org.json.JSONObject;

public class QRCodeScanner extends AppCompatActivity {
    private CodeScanner mCodeScanner;
    Activity activity = this;
    AppCompatActivity appCompatActivity = this;
    JSONObject json = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_q_r_code_scanner);
        CodeScannerView scannerView = findViewById(R.id.scanner_view);
        mCodeScanner = new CodeScanner(this, scannerView);
        mCodeScanner.setDecodeCallback(new DecodeCallback() {
            @Override
            public void onDecoded(@NonNull final Result result) {
                activity.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            json = new JSONObject(result.getText());
                            ItemToBuyDialog itemToBuyDialog = new ItemToBuyDialog(json, appCompatActivity);
                            itemToBuyDialog.show(getSupportFragmentManager(), "Item to buy dialog");
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                });
            }
        });

        mCodeScanner.startPreview();

        /*scannerView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    String str = "{\"itemPurchased\": \"item1\", \"cost\": \"114\", \"calorie\": \"1487\", \"fat\": \"150\", \"carbohydrate\": \"95\", \"protein\": \"1\", \"salt\": \"1\"}";
                    json = new JSONObject(str);
                    ItemToBuyDialog itemToBuyDialog = new ItemToBuyDialog(json, appCompatActivity);
                    itemToBuyDialog.show(getSupportFragmentManager(), "Item to buy dialog");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        });*/
    }

    @Override
    protected void onResume() {
        super.onResume();
        mCodeScanner.startPreview();
    }

    @Override
    protected void onPause() {
        mCodeScanner.releaseResources();
        super.onPause();
    }
}
