import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import json, os
from PIL import Image
from datetime import datetime
import hashlib
import threading
import time

# ============================================
# MUHIM! Bu yerda papka manzilini o'zgartiring!
# ============================================
# VARIANT 1: Google Drive (Tavsiya etiladi!)
# PROJECT_DIR = Path(r"C:\Users\YourName\Google Drive\kurs_platforma")

# VARIANT 2: Network Drive (Agar bir xil Wi-Fi bo'lsa)
# PROJECT_DIR = Path(r"\\COMPUTER-NAME\SharedFolder\kurs_platforma")

# VARIANT 3: USB Flash (Flash diskni ikki kompyuterga ulang)
# PROJECT_DIR = Path(r"E:\kurs_platforma")

# VARIANT 4: OneDrive
# PROJECT_DIR = Path(r"C:\Users\YourName\OneDrive\kurs_platforma")

# VARIANT 5: Dropbox
# PROJECT_DIR = Path(r"C:\Users\YourName\Dropbox\kurs_platforma")

# HOZIRGI (Default - ishlmaydi tarmoqda!)
PROJECT_DIR = Path(r"C:\kurs_platforma_SHARED")  # Ikkala kompyuterda BU PAPKA bo'lishi kerak!

# ============================================

CONFIG_FILE = PROJECT_DIR / "courses.json"
USERS_FILE = PROJECT_DIR / "users.json"
USER_DATA_FILE = PROJECT_DIR / "user_data.json"

PROJECT_DIR.mkdir(parents=True, exist_ok=True)

# Global o'zgaruvchilar
data = {}
users = {}
user_data = {}
current_user = None
auto_refresh_active = False

def load_data():
    """Ma'lumotlarni yuklash"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Load error: {e}")
    return {}

def save_data(data):
    """Ma'lumotlarni saqlash"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saqlandi: {CONFIG_FILE}")
    except Exception as e:
        print(f"Save error: {e}")
        messagebox.showerror("Xato", f"Saqlanmadi: {e}")

def load_users():
    try:
        if USERS_FILE.exists():
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"User save error: {e}")

def load_user_data():
    try:
        if USER_DATA_FILE.exists():
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_user_data(user_data):
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"User data save error: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# === AUTO REFRESH FUNCTION (REAL TIME) ===
def auto_refresh_data():
    """HAR 1 SEKUNDDA yangilaydi - REAL ONLINE!"""
    global data, auto_refresh_active
    while auto_refresh_active:
        try:
            new_data = load_data()
            if new_data != data:
                data.clear()
                data.update(new_data)
                print(f"🔄 Yangilandi! Kurslar: {len(data)}")
                # UI ni yangilash
                root.after(0, refresh_current_view)
        except Exception as e:
            print(f"Refresh error: {e}")
        time.sleep(1)  # Har 1 sekundda!

def start_auto_refresh():
    global auto_refresh_active
    auto_refresh_active = True
    thread = threading.Thread(target=auto_refresh_data, daemon=True)
    thread.start()
    print("✅ Auto-refresh yoqildi!")

def stop_auto_refresh():
    global auto_refresh_active
    auto_refresh_active = False
    print("⏹️ Auto-refresh to'xtatildi!")

def refresh_current_view():
    try:
        if current_user and hasattr(root, 'current_view'):
            if root.current_view == "student":
                show_all_videos_youtube_style(current_user)
            elif root.current_view == "teacher":
                refresh_teacher_courses()
    except Exception as e:
        print(f"View refresh error: {e}")

# Ma'lumotlarni yuklash
data = load_data()
users = load_users()
user_data = load_user_data()

print(f"📁 Papka: {PROJECT_DIR}")
print(f"📚 Yuklangan kurslar: {len(data)}")

# === GUI sozlamalar ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#48bb78",
    "danger": "#f56565",
    "warning": "#ed8936",
    "info": "#4299e1",
    "dark": "#1a202c",
    "teacher": "#f59e0b",
    "student": "#8b5cf6",
    "bg_dark": "#2d3748",
    "bg_darker": "#1a202c"
}

root = ctk.CTk()
root.title("🎓 Kurs Platformasi - ONLINE")
root.geometry("1200x700")
root.current_view = None

def create_gradient_frame(parent, height=100):
    frame = ctk.CTkFrame(parent, height=height, fg_color=COLORS["primary"])
    return frame

# === O'QUVCHI PANEL ===
def student_panel(username):
    global login_frame, main_area
    
    for widget in root.winfo_children():
        widget.destroy()
    
    root.current_view = "student"
    start_auto_refresh()
    
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True)

    # Top navbar
    top_nav = ctk.CTkFrame(main_frame, height=70, fg_color=COLORS["bg_darker"])
    top_nav.pack(fill="x", side="top")
    top_nav.pack_propagate(False)

    nav_left = ctk.CTkFrame(top_nav, fg_color="transparent")
    nav_left.pack(side="left", padx=20, pady=15)
    
    ctk.CTkLabel(nav_left, text="🎓", font=ctk.CTkFont(size=30)).pack(side="left", padx=(0, 10))
    ctk.CTkLabel(nav_left, text="Kurs Platformasi", 
                font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

    nav_right = ctk.CTkFrame(top_nav, fg_color="transparent")
    nav_right.pack(side="right", padx=20, pady=15)
    
    # Online indicator
    online_label = ctk.CTkLabel(nav_right, text="🟢 ONLINE", 
                                font=ctk.CTkFont(size=13, weight="bold"),
                                text_color=COLORS["success"])
    online_label.pack(side="left", padx=10)
    
    user_btn = ctk.CTkButton(nav_right, text=f"👤 {username}", 
                             fg_color=COLORS["student"],
                             hover_color=COLORS["secondary"],
                             width=150, height=40, corner_radius=20,
                             font=ctk.CTkFont(size=14, weight="bold"))
    user_btn.pack(side="right", padx=5)

    # Left sidebar
    sidebar = ctk.CTkFrame(main_frame, width=240, fg_color=COLORS["bg_darker"])
    sidebar.pack(side="left", fill="y")

    ctk.CTkLabel(sidebar, text="📺 Menyu", 
                font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

    def show_home():
        show_all_videos_youtube_style(username)

    def show_liked():
        show_liked_videos(username)

    def show_history():
        show_watch_history(username)

    def manual_refresh():
        global data
        data = load_data()
        show_all_videos_youtube_style(username)
        messagebox.showinfo("✅", f"Yangilandi!\nKurslar: {len(data)}")

    menu_items = [
        ("🏠 Bosh sahifa", show_home, COLORS["primary"]),
        ("❤️ Yoqtirganlar", show_liked, COLORS["danger"]),
        ("📜 Tarix", show_history, COLORS["info"]),
        ("🔄 Yangilash", manual_refresh, COLORS["warning"]),
    ]

    for text, command, color in menu_items:
        btn = ctk.CTkButton(sidebar, text=text, width=200, height=45,
                           command=command, corner_radius=10,
                           fg_color="transparent", hover_color=color,
                           anchor="w", font=ctk.CTkFont(size=14))
        btn.pack(pady=5, padx=20)

    # Debug info
    debug_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    debug_frame.pack(side="bottom", pady=20, padx=10)
    
    ctk.CTkLabel(debug_frame, text=f"📁 {PROJECT_DIR.name}", 
                font=ctk.CTkFont(size=10), text_color="gray").pack()

    # Main content
    main_area = ctk.CTkScrollableFrame(main_frame, fg_color=COLORS["bg_dark"])
    main_area.pack(fill="both", expand=True, padx=10, pady=10)

    show_all_videos_youtube_style(username)

def show_all_videos_youtube_style(username):
    """Barcha videolar - YouTube style"""
    global data
    data = load_data()
    
    for widget in main_area.winfo_children():
        widget.destroy()

    # Info header
    info_banner = ctk.CTkFrame(main_area, fg_color=COLORS["info"], corner_radius=10)
    info_banner.pack(fill="x", pady=10, padx=20)
    
    info_content = ctk.CTkFrame(info_banner, fg_color="transparent")
    info_content.pack(pady=15, padx=20)
    
    ctk.CTkLabel(info_content, text="ℹ️ Bu sahifa har 1 sekundda avtomatik yangilanadi", 
                font=ctk.CTkFont(size=14, weight="bold")).pack()
    ctk.CTkLabel(info_content, text=f"📁 Papka: {PROJECT_DIR}", 
                font=ctk.CTkFont(size=11), text_color="gray").pack()

    if not data:
        empty_frame = ctk.CTkFrame(main_area, fg_color="transparent")
        empty_frame.pack(expand=True)
        ctk.CTkLabel(empty_frame, text="📭", font=ctk.CTkFont(size=80)).pack(pady=20)
        ctk.CTkLabel(empty_frame, text="Hozircha videolar yo'q", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack()
        ctk.CTkLabel(empty_frame, text="Ustoz video qo'shganda bu yerda ko'rinadi (1 sekund ichida)", 
                    font=ctk.CTkFont(size=14), text_color="gray").pack(pady=10)
        return

    # Header
    header_frame = ctk.CTkFrame(main_area, fg_color="transparent")
    header_frame.pack(fill="x", pady=(10, 20), padx=20)
    
    ctk.CTkLabel(header_frame, text="🔥 Barcha videolar", 
                font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")
    
    total_videos = sum(len(c.get("videos", [])) for c in data.values())
    ctk.CTkLabel(header_frame, text=f"📹 {total_videos} ta video", 
                font=ctk.CTkFont(size=14), text_color="gray").pack(side="left", padx=20)

    # Kurslar va videolar
    for course_name, course_info in data.items():
        videos = course_info.get("videos", [])
        if not videos:
            continue

        course_section = ctk.CTkFrame(main_area, fg_color="transparent")
        course_section.pack(fill="x", pady=(10, 5), padx=20)
        
        ctk.CTkLabel(course_section, text=f"📚 {course_name}", 
                    font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        
        ctk.CTkLabel(course_section, text=f"{len(videos)} ta video", 
                    font=ctk.CTkFont(size=13), text_color="gray").pack(side="left", padx=15)

        # Video grid
        grid_container = ctk.CTkFrame(main_area, fg_color="transparent")
        grid_container.pack(fill="x", pady=(5, 20), padx=20)

        for idx, vid in enumerate(videos):
            row = idx // 3
            col = idx % 3

            video_card = ctk.CTkFrame(grid_container, width=360, height=340, 
                                     corner_radius=12, fg_color=COLORS["bg_darker"])
            video_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            video_card.grid_propagate(False)

            # Hover effect
            def on_enter(e, card=video_card):
                card.configure(fg_color="#374151")
            
            def on_leave(e, card=video_card):
                card.configure(fg_color=COLORS["bg_darker"])
            
            video_card.bind("<Enter>", on_enter)
            video_card.bind("<Leave>", on_leave)

            # Thumbnail
            thumb_frame = ctk.CTkFrame(video_card, height=200, corner_radius=10, fg_color="#000000")
            thumb_frame.pack(fill="x", padx=8, pady=8)
            thumb_frame.pack_propagate(False)

            if vid.get("image") and Path(vid["image"]).exists():
                try:
                    img = Image.open(vid["image"])
                    img = img.resize((344, 200), Image.Resampling.LANCZOS)
                    photo = ctk.CTkImage(img, size=(344, 200))
                    img_label = ctk.CTkLabel(thumb_frame, image=photo, text="")
                    img_label.pack(expand=True)
                    img_label.image = photo
                except:
                    ctk.CTkLabel(thumb_frame, text="🎬", font=ctk.CTkFont(size=70)).pack(expand=True)
            else:
                ctk.CTkLabel(thumb_frame, text="🎬", font=ctk.CTkFont(size=70)).pack(expand=True)

            # Info
            info_frame = ctk.CTkFrame(video_card, fg_color="transparent")
            info_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

            title_text = vid["title"]
            if len(title_text) > 50:
                title_text = title_text[:50] + "..."
            
            title_label = ctk.CTkLabel(info_frame, text=title_text, 
                                      font=ctk.CTkFont(size=15, weight="bold"),
                                      wraplength=320, anchor="w", justify="left")
            title_label.pack(fill="x", pady=(5, 3))

            # Stats
            stats_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            stats_frame.pack(fill="x", pady=3)

            likes = vid.get('likes', 0)
            ctk.CTkLabel(stats_frame, text=f"❤️ {likes}", 
                        font=ctk.CTkFont(size=12), text_color="gray").pack(side="left")

            # Actions
            actions = ctk.CTkFrame(info_frame, fg_color="transparent")
            actions.pack(fill="x", pady=(5, 0))

            def play_video(path=vid["video"], cn=course_name, i=idx, uname=username):
                if Path(path).exists():
                    try:
                        os.startfile(path)
                        video_key = f"{cn}_{i}"
                        if uname not in user_data:
                            user_data[uname] = {"watched": {}, "liked": []}
                        user_data[uname]["watched"][video_key] = {
                            "time": datetime.now().isoformat(),
                            "course": cn,
                            "title": vid["title"]
                        }
                        save_user_data(user_data)
                    except Exception as e:
                        messagebox.showerror("Xato", f"Video ochilmadi: {e}")
                else:
                    messagebox.showerror("Xato", "Video fayli topilmadi!")

            def like_video(cn=course_name, i=idx, uname=username):
                global data
                data = load_data()
                
                video_key = f"{cn}_{i}"
                if uname not in user_data:
                    user_data[uname] = {"watched": {}, "liked": []}
                
                if video_key not in user_data[uname].get("liked", []):
                    data[cn]["videos"][i]["likes"] = data[cn]["videos"][i].get("likes", 0) + 1
                    if "liked" not in user_data[uname]:
                        user_data[uname]["liked"] = []
                    user_data[uname]["liked"].append(video_key)
                    save_data(data)
                    save_user_data(user_data)
                    show_all_videos_youtube_style(username)
                    messagebox.showinfo("✅", "Video yoqtirildi!")
                else:
                    messagebox.showinfo("ℹ️", "Siz allaqachon bu videoni yoqtirdingiz!")

            play_btn = ctk.CTkButton(actions, text="▶️ Ko'rish", 
                                    command=play_video, height=38,
                                    fg_color=COLORS["success"], 
                                    hover_color=COLORS["primary"],
                                    font=ctk.CTkFont(size=13, weight="bold"))
            play_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

            like_btn = ctk.CTkButton(actions, text="❤️", width=55,
                                    command=like_video, height=38,
                                    fg_color=COLORS["danger"],
                                    hover_color=COLORS["warning"],
                                    font=ctk.CTkFont(size=16))
            like_btn.pack(side="right")

        for i in range(3):
            grid_container.grid_columnconfigure(i, weight=1)

def show_liked_videos(username):
    for widget in main_area.winfo_children():
        widget.destroy()

    ctk.CTkLabel(main_area, text="❤️ Yoqtirilgan videolar", 
                font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20, padx=20)

    if username not in user_data or not user_data[username].get("liked"):
        ctk.CTkLabel(main_area, text="Hozircha yoqtirilgan videolar yo'q", 
                    font=ctk.CTkFont(size=16), text_color="gray").pack(pady=30)
        return

    for video_key in user_data[username]["liked"]:
        try:
            course_name, idx = video_key.rsplit("_", 1)
            idx = int(idx)
            video = data[course_name]["videos"][idx]
            
            frame = ctk.CTkFrame(main_area, corner_radius=10, fg_color=COLORS["bg_darker"])
            frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(frame, text=f"❤️ {video['title']} - ({course_name})", 
                       font=ctk.CTkFont(size=15)).pack(pady=12, padx=20, anchor="w")
        except:
            pass

def show_watch_history(username):
    for widget in main_area.winfo_children():
        widget.destroy()

    ctk.CTkLabel(main_area, text="📜 Ko'rish tarixi", 
                font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20, padx=20)

    if username not in user_data or not user_data[username].get("watched"):
        ctk.CTkLabel(main_area, text="Hozircha tarix bo'sh", 
                    font=ctk.CTkFont(size=16), text_color="gray").pack(pady=30)
        return

    for video_key, info in sorted(user_data[username]["watched"].items(), 
                                  key=lambda x: x[1].get("time", ""), reverse=True):
        frame = ctk.CTkFrame(main_area, corner_radius=10, fg_color=COLORS["bg_darker"])
        frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(frame, text=f"✅ {info.get('title', 'Video')} - {info.get('course', '')}", 
                   font=ctk.CTkFont(size=15)).pack(pady=12, padx=20, anchor="w")

# === USTOZ PANEL ===
def teacher_panel(username):
    global login_frame, main_area
    
    for widget in root.winfo_children():
        widget.destroy()
    
    root.current_view = "teacher"
    start_auto_refresh()
    
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True)

    menu = ctk.CTkFrame(main_frame, width=250, corner_radius=0, fg_color=COLORS["bg_darker"])
    menu.pack(side="left", fill="y")

    header = create_gradient_frame(menu, height=120)
    header.pack(fill="x", pady=(0, 20))
    
    ctk.CTkLabel(header, text="👨‍🏫", font=ctk.CTkFont(size=50)).pack(pady=(15, 5))
    ctk.CTkLabel(header, text="Ustoz Panel", 
                font=ctk.CTkFont(size=20, weight="bold")).pack()
    ctk.CTkLabel(header, text=username, 
                font=ctk.CTkFont(size=14), text_color="gray").pack(pady=(5, 10))

    def add_course():
        dialog = ctk.CTkInputDialog(text="Yangi kurs nomi:", title="Kurs yaratish")
        name = dialog.get_input()
        if not name:
            return
        if name in data:
            messagebox.showerror("Xato", "Bu kurs allaqachon mavjud!")
            return
        data[name] = {"videos": [], "created": datetime.now().isoformat(), "teacher": username}
        save_data(data)
        print(f"✅ Kurs yaratildi: {name}")
        refresh_teacher_courses()
        messagebox.showinfo("✅", f"'{name}' kursi yaratildi!\nO'quvchilar 1 sekundda ko'radi!")

    def add_video():
        global data
        data = load_data()
        
        if not data:
            messagebox.showinfo("Eslatma", "Avval kurs yarating!")
            return

        select_window = ctk.CTkToplevel(root)
        select_window.title("Kurs tanlash")
        select_window.geometry("450x550")
        select_window.grab_set()
        
        header = create_gradient_frame(select_window, height=80)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="📚 Kurs tanlang", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=25)
        
        scroll_frame = ctk.CTkScrollableFrame(select_window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        selected_course = ctk.StringVar()
        
        for course_name in data.keys():
            radio_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
            radio_frame.pack(fill="x", pady=5)
            
            radio = ctk.CTkRadioButton(radio_frame, text=course_name, 
                                      variable=selected_course, value=course_name,
                                      font=ctk.CTkFont(size=15))
            radio.pack(pady=10, padx=15, anchor="w")
        
        def continue_adding():
            choice = selected_course.get()
            if not choice:
                messagebox.showerror("Xato", "Kurs tanlanmadi!")
                return
            select_window.destroy()
            
            title = ctk.CTkInputDialog(text="Video nomini kiriting:", 
                                      title="Yangi video").get_input()
            if not title:
                return

            video_path = filedialog.askopenfilename(
                title="Video fayl tanlang", 
                filetypes=[("Video files", "*.mp4;*.mkv;*.avi;*.mov")]
            )
            if not video_path:
                return

            image_path = filedialog.askopenfilename(
                title="Rasm tanlang (ixtiyoriy)", 
                filetypes=[("Rasm", "*.jpg;*.png;*.jpeg")]
            )

            data[choice]["videos"].append({
                "title": title,
                "video": video_path,
                "image": image_path if image_path else "",
                "likes": 0,
                "added": datetime.now().isoformat(),
                "teacher": username
            })
            save_data(data)
            print(f"✅ Video qo'shildi: {title} -> {choice}")
            refresh_teacher_courses()
            messagebox.showinfo("✅ TAYYOR!", 
                              f"Video qo'shildi!\n\nBarcha o'quvchilar bu videoni 1 sekund ichida ko'radi!\n\nPapka: {PROJECT_DIR}")
        
        btn_frame = ctk.CTkFrame(select_window, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(btn_frame, text="Davom etish", height=45,
                     command=continue_adding, fg_color=COLORS["primary"],
                     font=ctk.CTkFont(size=15, weight="bold")).pack(fill="x")

    def delete_course():
        global data
        data = load_data()
        
        if not data:
            messagebox.showinfo("Eslatma", "O'chiriladigan kurs yo'q!")
            return
            
        dialog = ctk.CTkInputDialog(text=f"O'chiriladigan kurs:\n{', '.join(data.keys())}", 
                                   title="Kurs o'chirish")
        name = dialog.get_input()
        if name in data:
            if messagebox.askyesno("Tasdiqlash", f"'{name}' kursini o'chirishni xohlaysizmi?"):
                del data[name]
                save_data(data)
                refresh_teacher_courses()
                messagebox.showinfo("✅", "Kurs o'chirildi!")
        else:
            messagebox.showerror("Xato", "Kurs topilmadi!")

    def show_statistics():
        stats_window = ctk.CTkToplevel(root)
        stats_window.title("📊 Statistika")
        stats_window.geometry("550x450")
        stats_window.grab_set()
        
        header = create_gradient_frame(stats_window, height=80)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="📊 Platforma statistikasi", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=25)
        
        total_courses = len(data)
        total_videos = sum(len(c.get("videos", [])) for c in data.values())
        total_likes = sum(sum(v.get("likes", 0) for v in c.get("videos", [])) 
                         for c in data.values())
        total_students = len([u for u, info in users.items() if info.get("role") == "student"])
        
        stats_frame = ctk.CTkScrollableFrame(stats_window, fg_color="transparent")
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        stats_data = [
            ("📚 Jami kurslar", total_courses, COLORS["primary"]),
            ("🎬 Jami videolar", total_videos, COLORS["info"]),
            ("❤️ Jami likelar", total_likes, COLORS["danger"]),
            ("👥 O'quvchilar", total_students, COLORS["success"])
        ]
        
        for label, value, color in stats_data:
            frame = ctk.CTkFrame(stats_frame, corner_radius=10, fg_color=color)
            frame
            pack(fill="x", pady=8)
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=16),
                        text_color="white").pack(side="left", padx=20, pady=20)
            ctk.CTkLabel(frame, text=str(value), font=ctk.CTkFont(size=24, weight="bold"),
                        text_color="white").pack(side="right", padx=20, pady=20)

    def refresh_teacher_courses():
        global data
        data = load_data()
        
        for widget in main_area.winfo_children():
            widget.destroy()

        # Info banner
        info_banner = ctk.CTkFrame(main_area, fg_color=COLORS["info"], corner_radius=10)
        info_banner.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(info_banner, text=f"📁 Papka: {PROJECT_DIR} | 🔄 Auto-refresh: Yoqilgan", 
                    font=ctk.CTkFont(size=12)).pack(pady=10)

        if not data:
            empty_frame = ctk.CTkFrame(main_area, fg_color="transparent")
            empty_frame.pack(expand=True)
            ctk.CTkLabel(empty_frame, text="📭", font=ctk.CTkFont(size=80)).pack(pady=20)
            ctk.CTkLabel(empty_frame, text="Hozircha kurslar yo'q", 
                        font=ctk.CTkFont(size=24, weight="bold")).pack()
            return

        header_frame = ctk.CTkFrame(main_area, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 20), padx=10)
        
        ctk.CTkLabel(header_frame, text="📚 Barcha kurslar", 
                    font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")

        for course_name, course_info in data.items():
            course_frame = ctk.CTkFrame(main_area, corner_radius=15, 
                                       fg_color=COLORS["bg_darker"])
            course_frame.pack(fill="x", pady=10, padx=10)

            info_frame = ctk.CTkFrame(course_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
            
            title_label = ctk.CTkLabel(info_frame, text=f"🎓 {course_name}", 
                                       font=ctk.CTkFont(size=22, weight="bold"))
            title_label.pack(anchor="w")
            
            video_count = len(course_info.get("videos", []))
            total_likes = sum(v.get("likes", 0) for v in course_info.get("videos", []))
            
            stats_label = ctk.CTkLabel(info_frame, 
                                       text=f"📹 {video_count} video  •  ❤️ {total_likes} like",
                                       font=ctk.CTkFont(size=14), text_color="gray")
            stats_label.pack(anchor="w", pady=(5, 0))

            btn_frame = ctk.CTkFrame(course_frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=20, pady=20)

            def view_videos(cn=course_name):
                show_teacher_videos(cn, username)

            view_btn = ctk.CTkButton(btn_frame, text="👁️ Ko'rish", command=view_videos, 
                                    width=130, height=40, corner_radius=10,
                                    fg_color=COLORS["info"])
            view_btn.pack()

    def show_teacher_videos(course_name, teacher_username):
        global data
        data = load_data()
        
        for widget in main_area.winfo_children():
            widget.destroy()

        header_frame = create_gradient_frame(main_area, height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, pady=20)
        
        ctk.CTkLabel(header_content, text=f"📘 {course_name}", 
                    font=ctk.CTkFont(size=28, weight="bold")).pack()
        
        videos = data[course_name].get("videos", [])
        ctk.CTkLabel(header_content, text=f"{len(videos)} ta video",
                    font=ctk.CTkFont(size=15), text_color="gray").pack(pady=(5, 0))

        nav_frame = ctk.CTkFrame(main_area, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        back_btn = ctk.CTkButton(nav_frame, text="⬅️ Orqaga", width=120, height=40,
                                command=refresh_teacher_courses, corner_radius=10,
                                fg_color=COLORS["info"])
        back_btn.pack(side="left")

        if not videos:
            empty_frame = ctk.CTkFrame(main_area, fg_color="transparent")
            empty_frame.pack(expand=True)
            ctk.CTkLabel(empty_frame, text="🎬", font=ctk.CTkFont(size=80)).pack(pady=20)
            ctk.CTkLabel(empty_frame, text="Hozircha video yo'q", 
                        font=ctk.CTkFont(size=24, weight="bold")).pack()
            return

        videos_container = ctk.CTkScrollableFrame(main_area, fg_color="transparent")
        videos_container.pack(fill="both", expand=True, padx=10, pady=10)

        for idx, vid in enumerate(videos):
            video_card = ctk.CTkFrame(videos_container, corner_radius=15,
                                     fg_color=COLORS["bg_darker"])
            video_card.pack(fill="x", pady=8)
            
            content_frame = ctk.CTkFrame(video_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=15, pady=15)

            image_frame = ctk.CTkFrame(content_frame, width=160, height=100, corner_radius=10)
            image_frame.pack(side="left", padx=(0, 15))
            image_frame.pack_propagate(False)
            
            if vid.get("image") and Path(vid["image"]).exists():
                try:
                    img = Image.open(vid["image"])
                    img = img.resize((160, 100), Image.Resampling.LANCZOS)
                    photo = ctk.CTkImage(img, size=(160, 100))
                    img_label = ctk.CTkLabel(image_frame, image=photo, text="")
                    img_label.pack(expand=True)
                    img_label.image = photo
                except:
                    ctk.CTkLabel(image_frame, text="🎞️", 
                               font=ctk.CTkFont(size=40)).pack(expand=True)
            else:
                ctk.CTkLabel(image_frame, text="🎞️", 
                            font=ctk.CTkFont(size=40)).pack(expand=True)

            info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True)
            
            title_label = ctk.CTkLabel(info_frame, text=vid["title"], 
                                       font=ctk.CTkFont(size=18, weight="bold"))
            title_label.pack(anchor="w")
            
            stats_text = f"❤️ {vid.get('likes', 0)} like"
            ctk.CTkLabel(info_frame, text=stats_text, 
                        font=ctk.CTkFont(size=14), text_color="gray").pack(anchor="w", pady=(5, 0))

            btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=10)

            def play_video(path=vid["video"]):
                if Path(path).exists():
                    try:
                        os.startfile(path)
                    except:
                        messagebox.showerror("Xato", "Video ochilmadi!")
                else:
                    messagebox.showerror("Xato", "Video topilmadi!")

            def delete_video(cn=course_name, i=idx):
                if messagebox.askyesno("Tasdiqlash", "Videoni o'chirishni xohlaysizmi?"):
                    data[cn]["videos"].pop(i)
                    save_data(data)
                    show_teacher_videos(cn, teacher_username)

            play_btn = ctk.CTkButton(btn_frame, text="▶️ Ko'rish", width=110, height=38,
                                    command=play_video, corner_radius=10,
                                    fg_color=COLORS["success"])
            play_btn.pack(pady=2)

            delete_btn = ctk.CTkButton(btn_frame, text="🗑️ O'chirish", width=110, height=38,
                                      command=delete_video, corner_radius=10,
                                      fg_color=COLORS["danger"])
            delete_btn.pack(pady=2)

    menu_buttons = [
        ("📘 Kurs yaratish", add_course, COLORS["primary"]),
        ("🎞️ Video qo'shish", add_video, COLORS["success"]),
        ("❌ Kurs o'chirish", delete_course, COLORS["danger"]),
        ("📊 Statistika", show_statistics, COLORS["info"]),
        ("🔄 Yangilash", refresh_teacher_courses, COLORS["warning"])
    ]

    for text, command, color in menu_buttons:
        btn = ctk.CTkButton(menu, text=text, width=220, height=48,
                           command=command, corner_radius=10,
                           fg_color=color, hover_color=COLORS["secondary"],
                           font=ctk.CTkFont(size=15, weight="bold"))
        btn.pack(pady=8, padx=15)

    main_area = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
    main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    refresh_teacher_courses()


# === LOGIN / SIGNUP ===
def show_login_page():
    global login_frame
    
    for widget in root.winfo_children():
        widget.destroy()
    
    root.current_view = None
    stop_auto_refresh()
    
    login_frame = ctk.CTkFrame(root, fg_color=COLORS["bg_dark"])
    login_frame.pack(fill="both", expand=True)

    login_header = create_gradient_frame(login_frame, height=220)
    login_header.pack(fill="x")

    header_content = ctk.CTkFrame(login_header, fg_color="transparent")
    header_content.pack(expand=True, pady=30)

    ctk.CTkLabel(header_content, text="🎓", font=ctk.CTkFont(size=80)).pack()
    ctk.CTkLabel(header_content, text="Kurs Platformasi", 
                font=ctk.CTkFont(size=38, weight="bold")).pack(pady=10)

    form_frame = ctk.CTkFrame(login_frame, corner_radius=0, fg_color="transparent")
    form_frame.pack(expand=True, pady=40)

    ctk.CTkLabel(form_frame, text="🔐 Tizimga kirish", 
                font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(0, 30))

    username_entry = ctk.CTkEntry(form_frame, placeholder_text="👤 Login", 
                                 width=350, height=55, corner_radius=10,
                                 font=ctk.CTkFont(size=16),
                                 border_width=2, border_color=COLORS["primary"])
    username_entry.pack(pady=12)

    password_entry = ctk.CTkEntry(form_frame, placeholder_text="🔒 Parol", show="*", 
                                 width=350, height=55, corner_radius=10,
                                 font=ctk.CTkFont(size=16),
                                 border_width=2, border_color=COLORS["primary"])
    password_entry.pack(pady=12)

    def check_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Xato", "Login va parolni kiriting!")
            return
        
        if username not in users:
            messagebox.showerror("Xato", "Foydalanuvchi topilmadi!")
            return
        
        if users[username]["password"] != hash_password(password):
            messagebox.showerror("Xato", "Parol noto'g'ri!")
            return
        
        global current_user
        current_user = username
        role = users[username]["role"]
        
        if role == "teacher":
            teacher_panel(username)
        else:
            student_panel(username)

    login_btn = ctk.CTkButton(form_frame, text="🔐 Kirish", width=350, height=55,
                             command=check_login, corner_radius=10,
                             fg_color=COLORS["primary"], hover_color=COLORS["secondary"],
                             font=ctk.CTkFont(size=18, weight="bold"))
    login_btn.pack(pady=20)

    signup_frame = ctk.CTkFrame(form_frame, fg_color=COLORS["success"], 
                               corner_radius=10, height=55)
    signup_frame.pack(pady=10, fill="x")
    signup_frame.pack_propagate(False)
    
    signup_btn = ctk.CTkButton(signup_frame, text="Hisobingiz yo'qmi? Ro'yxatdan o'ting", 
                               command=show_signup_page, 
                               fg_color="transparent", hover_color=COLORS["primary"],
                               font=ctk.CTkFont(size=15, weight="bold"),
                               text_color="white")
    signup_btn.pack(expand=True, fill="both")

    def on_enter(event):
        check_login()
    
    root.bind('<Return>', on_enter)


def show_signup_page():
    global login_frame
    
    for widget in root.winfo_children():
        widget.destroy()
    
    root.current_view = None
    stop_auto_refresh()
    
    login_frame = ctk.CTkFrame(root, fg_color=COLORS["bg_dark"])
    login_frame.pack(fill="both", expand=True)

    signup_header = create_gradient_frame(login_frame, height=180)
    signup_header.pack(fill="x")

    header_content = ctk.CTkFrame(signup_header, fg_color="transparent")
    header_content.pack(expand=True, pady=20)

    ctk.CTkLabel(header_content, text="📝", font=ctk.CTkFont(size=70)).pack()
    ctk.CTkLabel(header_content, text="Ro'yxatdan o'tish", 
                font=ctk.CTkFont(size=36, weight="bold")).pack()

    # SCROLLABLE FRAME - Asosiy o'zgarish bu yerda!
    scrollable_container = ctk.CTkScrollableFrame(login_frame, fg_color="transparent")
    scrollable_container.pack(fill="both", expand=True, padx=20, pady=20)

    form_frame = ctk.CTkFrame(scrollable_container, corner_radius=0, fg_color="transparent")
    form_frame.pack(expand=True, pady=20)

    ctk.CTkLabel(form_frame, text="✨ Yangi hisob yaratish", 
                font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(0, 20))

    username_entry = ctk.CTkEntry(form_frame, placeholder_text="👤 Login", 
                                 width=380, height=52, corner_radius=10,
                                 font=ctk.CTkFont(size=15),
                                 border_width=2, border_color=COLORS["primary"])
    username_entry.pack(pady=8)

    password_entry = ctk.CTkEntry(form_frame, placeholder_text="🔒 Parol", show="*", 
                                 width=380, height=52, corner_radius=10,
                                 font=ctk.CTkFont(size=15),
                                 border_width=2, border_color=COLORS["primary"])
    password_entry.pack(pady=8)

    confirm_password_entry = ctk.CTkEntry(form_frame, placeholder_text="🔒 Parolni tasdiqlang", show="*", 
                                         width=380, height=52, corner_radius=10,
                                         font=ctk.CTkFont(size=15),
                                         border_width=2, border_color=COLORS["primary"])
    confirm_password_entry.pack(pady=8)

    ctk.CTkLabel(form_frame, text="Kim sifatida ro'yxatdan o'tasiz?", 
                font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(15, 10))

    role_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    role_frame.pack(pady=10)

    selected_role = ctk.StringVar(value="student")

    teacher_btn = ctk.CTkButton(role_frame, text="👨‍🏫 Ustoz", width=180, height=90,
                               corner_radius=15, fg_color=COLORS["teacher"],
                               hover_color=COLORS["warning"],
                               font=ctk.CTkFont(size=19, weight="bold"),
                               command=lambda: selected_role.set("teacher"))
    teacher_btn.pack(side="left", padx=10)

    student_btn = ctk.CTkButton(role_frame, text="👨‍🎓 O'quvchi", width=180, height=90,
                               corner_radius=15, fg_color=COLORS["student"],
                               hover_color=COLORS["secondary"],
                               font=ctk.CTkFont(size=19, weight="bold"),
                               command=lambda: selected_role.set("student"))
    student_btn.pack(side="left", padx=10)

    role_indicator = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(size=15))
    role_indicator.pack(pady=5)

    def update_role_indicator():
        role = selected_role.get()
        if role == "teacher":
            role_indicator.configure(text="✅ Ustoz tanlandi", text_color=COLORS["teacher"])
            teacher_btn.configure(border_width=3, border_color="white")
            student_btn.configure(border_width=0)
        else:
            role_indicator.configure(text="✅ O'quvchi tanlandi", text_color=COLORS["student"])
            student_btn.configure(border_width=3, border_color="white")
            teacher_btn.configure(border_width=0)
        root.after(100, update_role_indicator)

    update_role_indicator()

    def create_account():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        confirm_password = confirm_password_entry.get().strip()
        role = selected_role.get()
        
        if not username or not password or not confirm_password:
            messagebox.showerror("Xato", "Barcha maydonlarni to'ldiring!")
            return
        
        if len(username) < 3:
            messagebox.showerror("Xato", "Login kamida 3 ta belgidan iborat bo'lishi kerak!")
            return
        
        if len(password) < 4:
            messagebox.showerror("Xato", "Parol kamida 4 ta belgidan iborat bo'lishi kerak!")
            return
        
        if password != confirm_password:
            messagebox.showerror("Xato", "Parollar mos kelmadi!")
            return
        
        if username in users:
            messagebox.showerror("Xato", "Bu login band!")
            return
        
        users[username] = {
            "password": hash_password(password),
            "role": role,
            "created": datetime.now().isoformat()
        }
        save_users(users)
        
        messagebox.showinfo("✅ Muvaffaqiyat", f"Hisob yaratildi!\nEndi tizimga kiring.")
        show_login_page()

    signup_btn = ctk.CTkButton(form_frame, text="📝 Ro'yxatdan o'tish", width=380, height=52,
                              command=create_account, corner_radius=10,
                              fg_color=COLORS["success"], hover_color=COLORS["primary"],
                              font=ctk.CTkFont(size=18, weight="bold"))
    signup_btn.pack(pady=20)

    login_link_frame = ctk.CTkFrame(form_frame, fg_color=COLORS["info"], 
                                   corner_radius=10, height=52)
    login_link_frame.pack(fill="x", pady=(0, 20))
    login_link_frame.pack_propagate(False)
    
    login_link = ctk.CTkButton(login_link_frame, text="Hisobingiz bormi? Kirish", 
                              command=show_login_page,
                              fg_color="transparent", hover_color=COLORS["primary"],
                              font=ctk.CTkFont(size=15, weight="bold"),
                              text_color="white")
    login_link.pack(expand=True, fill="both")


# === BOSHLASH ===
print("="*60)
print("🎓 KURS PLATFORMASI - ONLINE REJIM")
print("="*60)
print(f"📁 Papka: {PROJECT_DIR}")
print(f"📚 Yuklangan kurslar: {len(data)}")
print(f"👥 Foydalanuvchilar: {len(users)}")
print("="*60)
print("\n⚠️  MUHIM ESLATMA:")
print("1. Ikkala kompyuterda BIR XILL papkadan foydalaning!")
print("2. Google Drive, OneDrive yoki Network papka ishlatishni tavsiya qilamiz")
print("3. Kodning 17-qator: PROJECT_DIR o'zgaruvchisini o'zgartiring")
print("="*60)

show_login_page()
root.mainloop()