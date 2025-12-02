// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_macos_permissions::init())
        .plugin(tauri_plugin_log::Builder::default().level(log::LevelFilter::Info).build())
        .setup(|app| {
            use tauri::Manager;

            // Get the HUD window (created via tauri.conf.json)
            if let Some(hud_window) = app.get_webview_window("hud") {
                // Position in top-right corner
                if let Ok(monitor) = hud_window.current_monitor() {
                    if let Some(monitor) = monitor {
                        let screen_size = monitor.size();
                        let window_size = hud_window.outer_size()?;
                        
                        // 20px padding from edges
                        let x = screen_size.width as i32 - window_size.width as i32 - 20;
                        let y = 20;
                        
                        hud_window.set_position(tauri::PhysicalPosition::new(x, y))?;
                    }
                }
            }

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                if window.label() == "main" {
                    std::process::exit(0);
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

