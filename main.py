
import os
import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.clock import Clock

try:
    from plyer import filechooser
except Exception:
    filechooser = None

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "students.db")
TEMPLATE = os.path.join(BASE, "assets", "card_template.jpg")

# ---------- Theme ----------
NAVY = (0.035, 0.20, 0.45, 1)
BLUE = (0.08, 0.43, 0.75, 1)
LIGHT = (0.95, 0.97, 0.99, 1)
WHITE = (1, 1, 1, 1)
TEXT = (0.10, 0.14, 0.20, 1)
MUTED = (0.38, 0.45, 0.54, 1)
GREEN = (0.10, 0.55, 0.34, 1)
RED = (0.75, 0.12, 0.12, 1)

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            university_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            college TEXT,
            major TEXT,
            semester TEXT,
            level TEXT,
            photo TEXT,
            created_at TEXT
        )
    """)
    con.commit()
    con.close()

def query(sql, args=(), one=False):
    con = sqlite3.connect(DB)
    cur = con.execute(sql, args)
    rows = cur.fetchone() if one else cur.fetchall()
    con.close()
    return rows

def execute(sql, args=()):
    con = sqlite3.connect(DB)
    cur = con.execute(sql, args)
    con.commit()
    last = cur.lastrowid
    con.close()
    return last

class Card(Widget):
    def __init__(self, bg=(1,1,1,1), radius=18, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._sync, size=self._sync)
    def _sync(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

class Title(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("font_size", "22sp")
        kwargs.setdefault("bold", True)
        kwargs.setdefault("color", WHITE)
        kwargs.setdefault("halign", "right")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)

class AppButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(48))
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_color", BLUE)
        kwargs.setdefault("color", WHITE)
        kwargs.setdefault("font_size", "15sp")
        super().__init__(**kwargs)

class Input(TextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(46))
        kwargs.setdefault("multiline", False)
        kwargs.setdefault("font_size", "15sp")
        kwargs.setdefault("padding", [dp(12), dp(10)])
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_active", "")
        kwargs.setdefault("foreground_color", TEXT)
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*WHITE)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            Color(0.78,0.84,0.91,1)
            self.border = Line(rounded_rectangle=(self.x,self.y,self.width,self.height,10), width=1)
        self.bind(pos=self._sync, size=self._sync)
    def _sync(self, *_):
        self.bg.pos, self.bg.size = self.pos, self.size
        self.border.rounded_rectangle = (self.x,self.y,self.width,self.height,10)

class Dashboard(Screen):
    def on_pre_enter(self, *_):
        self.refresh()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        header = BoxLayout(size_hint_y=None, height=dp(88), padding=[dp(18),dp(10)])
        with header.canvas.before:
            Color(*NAVY)
            header.bg = RoundedRectangle(pos=header.pos, size=header.size, radius=[dp(20)])
        header.bind(pos=lambda *_: setattr(header.bg, "pos", header.pos),
                    size=lambda *_: setattr(header.bg, "size", header.size))
        header.add_widget(Title(text="جامعة المغتربين\nنظام بطاقات الطلاب"))
        root.add_widget(header)

        scroll = ScrollView(do_scroll_x=False)
        body = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(14), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        self.stats = Label(text="", color=TEXT, font_size="16sp", halign="right", valign="middle",
                           size_hint_y=None, height=dp(85))
        stat_card = Card(bg=WHITE, radius=16, size_hint_y=None, height=dp(85))
        stat_card.add_widget(self.stats)
        body.add_widget(stat_card)

        body.add_widget(Label(text="الخدمات الرئيسية", color=TEXT, font_size="19sp",
                              bold=True, halign="right", size_hint_y=None, height=dp(35)))

        for txt, screen in [
            ("➕   إضافة طالب جديد", "student_form"),
            ("👥   إدارة الطلاب والبحث", "students"),
            ("🪪   معاينة بطاقة طالب", "students"),
        ]:
            b = AppButton(text=txt)
            b.background_color = NAVY if "إضافة" in txt else BLUE
            b.bind(on_release=lambda _b, s=screen: self.go(s))
            body.add_widget(b)

        hint = Label(text="يمكنك إضافة صورة الطالب ثم إصدار البطاقة بنفس التصميم المرفق.",
                     color=MUTED, font_size="13sp", halign="right",
                     text_size=(None,None), size_hint_y=None, height=dp(60))
        body.add_widget(hint)

        scroll.add_widget(body)
        root.add_widget(scroll)
        self.add_widget(root)

    def go(self, s):
        self.manager.current = s

    def refresh(self):
        total = query("SELECT COUNT(*) FROM students", one=True)[0]
        self.stats.text = f"عدد الطلاب المسجلين:  {total}\n\nآخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

class Students(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        bar = BoxLayout(size_hint_y=None, height=dp(74), padding=[dp(12),dp(8)], spacing=dp(8))
        back = AppButton(text="‹", size_hint_x=None, width=dp(48))
        back.bind(on_release=lambda *_: self.back())
        bar.add_widget(back)
        self.search = Input(hint_text="ابحث بالاسم أو الرقم الجامعي")
        bar.add_widget(self.search)
        sb = AppButton(text="بحث", size_hint_x=None, width=dp(80))
        sb.bind(on_release=lambda *_: self.refresh())
        bar.add_widget(sb)
        root.add_widget(bar)

        self.listbox = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12), size_hint_y=None)
        self.listbox.bind(minimum_height=self.listbox.setter("height"))
        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(self.listbox)
        root.add_widget(scroll)

        add = AppButton(text="＋ إضافة طالب")
        add.bind(on_release=lambda *_: self.open_new())
        root.add_widget(add)
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self.refresh()

    def back(self):
        self.manager.current = "dashboard"

    def refresh(self):
        self.listbox.clear_widgets()
        q = self.search.text.strip()
        if q:
            rows = query("""SELECT * FROM students
                WHERE name LIKE ? OR university_id LIKE ?
                ORDER BY id DESC""", (f"%{q}%",f"%{q}%"))
        else:
            rows = query("SELECT * FROM students ORDER BY id DESC")

        if not rows:
            self.listbox.add_widget(Label(text="لا توجد بيانات طلاب.", color=MUTED,
                                          size_hint_y=None, height=dp(80)))
            return

        for s in rows:
            self.listbox.add_widget(StudentRow(s, self))

    def open_new(self):
        self.manager.get_screen("student_form").load_student(None)
        self.manager.current = "student_form"

class StudentRow(Card):
    def __init__(self, student, owner, **kwargs):
        super().__init__(bg=WHITE, radius=14, size_hint_y=None, height=dp(92), **kwargs)
        self.student = student
        self.owner = owner
        layout = BoxLayout(padding=dp(10), spacing=dp(8))
        info = BoxLayout(orientation="vertical")
        info.add_widget(Label(text=student[2], color=TEXT, bold=True, font_size="16sp", halign="right"))
        info.add_widget(Label(text=f"{student[1]}  |  {student[3] or '—'}", color=MUTED,
                              font_size="12sp", halign="right"))
        layout.add_widget(info)
        edit = AppButton(text="فتح", size_hint_x=None, width=dp(75))
        edit.bind(on_release=lambda *_: self.open())
        layout.add_widget(edit)
        self.add_widget(layout)

    def open(self):
        self.owner.manager.get_screen("student_form").load_student(self.student)
        self.owner.manager.current = "student_form"

class StudentForm(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.student_id = None
        self.photo_path = ""

        root = BoxLayout(orientation="vertical")
        top = BoxLayout(size_hint_y=None, height=dp(68), padding=[dp(12),dp(8)])
        back = AppButton(text="‹", size_hint_x=None, width=dp(48))
        back.bind(on_release=lambda *_: self.back())
        top.add_widget(back)
        top.add_widget(Title(text="بيانات الطالب"))
        root.add_widget(top)

        scroll = ScrollView(do_scroll_x=False)
        form = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16), size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        self.inputs = {}
        fields = [
            ("اسم الطالب", "name"),
            ("الرقم الجامعي", "university_id"),
            ("الكلية", "college"),
            ("التخصص", "major"),
            ("الفصل الدراسي", "semester"),
            ("المستوى", "level"),
        ]
        for label, key in fields:
            form.add_widget(Label(text=label, color=TEXT, font_size="14sp",
                                  halign="right", size_hint_y=None, height=dp(28)))
            inp = Input(hint_text=label)
            self.inputs[key] = inp
            form.add_widget(inp)

        photo_box = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(8))
        self.photo_status = Label(text="لم يتم اختيار صورة", color=MUTED, halign="right")
        photo_box.add_widget(self.photo_status)
        pb = AppButton(text="📷 اختيار صورة", size_hint_x=None, width=dp(145))
        pb.bind(on_release=lambda *_: self.choose_photo())
        photo_box.add_widget(pb)
        form.add_widget(photo_box)

        save = AppButton(text="حفظ البيانات")
        save.background_color = GREEN
        save.bind(on_release=lambda *_: self.save())
        form.add_widget(save)

        preview = AppButton(text="معاينة البطاقة")
        preview.bind(on_release=lambda *_: self.preview())
        form.add_widget(preview)

        delete = AppButton(text="حذف الطالب")
        delete.background_color = RED
        delete.bind(on_release=lambda *_: self.delete())
        form.add_widget(delete)

        scroll.add_widget(form)
        root.add_widget(scroll)
        self.add_widget(root)

    def back(self):
        self.manager.current = "students"

    def load_student(self, s):
        self.student_id = s[0] if s else None
        self.photo_path = s[7] if s else ""
        for key, inp in self.inputs.items():
            inp.text = (s[{"university_id":1,"name":2,"college":3,"major":4,"semester":5,"level":6}[key]] or "") if s else ""
        self.photo_status.text = os.path.basename(self.photo_path) if self.photo_path else "لم يتم اختيار صورة"

    def choose_photo(self):
        if filechooser:
            try:
                result = filechooser.open_file(filters=["*.png","*.jpg","*.jpeg"])
                if result:
                    self.photo_path = result[0]
                    self.photo_status.text = os.path.basename(self.photo_path)
            except Exception as e:
                self.photo_status.text = "تعذر اختيار الصورة"
        else:
            self.photo_status.text = "يحتاج اختيار الملفات من Android"

    def save(self):
        name = self.inputs["name"].text.strip()
        uid = self.inputs["university_id"].text.strip()
        if not name or not uid:
            self.alert("الاسم والرقم الجامعي مطلوبان.")
            return
        data = (
            uid, name, self.inputs["college"].text.strip(),
            self.inputs["major"].text.strip(), self.inputs["semester"].text.strip(),
            self.inputs["level"].text.strip(), self.photo_path
        )
        try:
            if self.student_id:
                execute("""UPDATE students SET university_id=?,name=?,college=?,major=?,
                    semester=?,level=?,photo=? WHERE id=?""", (*data, self.student_id))
            else:
                execute("""INSERT INTO students(university_id,name,college,major,semester,level,photo,created_at)
                    VALUES(?,?,?,?,?,?,?,?)""", (*data, datetime.now().isoformat()))
            self.alert("تم حفظ بيانات الطالب بنجاح.")
        except sqlite3.IntegrityError:
            self.alert("الرقم الجامعي موجود مسبقًا.")

    def delete(self):
        if not self.student_id:
            return
        if self.student_id:
            execute("DELETE FROM students WHERE id=?", (self.student_id,))
            self.alert("تم حذف الطالب.")
            self.back()

    def preview(self):
        uid = self.inputs["university_id"].text.strip()
        name = self.inputs["name"].text.strip()
        if not name or not uid:
            self.alert("أدخل الاسم والرقم الجامعي أولًا.")
            return
        student = (self.student_id or 0, uid, name,
                   self.inputs["college"].text.strip(),
                   self.inputs["major"].text.strip(),
                   self.inputs["semester"].text.strip(),
                   self.inputs["level"].text.strip(), self.photo_path, "")
        screen = self.manager.get_screen("preview")
        screen.load_student(student)
        self.manager.current = "preview"

    def alert(self, msg):
        Popup(title="نظام بطاقات الطلاب",
              content=Label(text=msg, color=TEXT),
              size_hint=(.85,.28)).open()

class Preview(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        top = BoxLayout(size_hint_y=None, height=dp(68), padding=[dp(12),dp(8)])
        back = AppButton(text="‹", size_hint_x=None, width=dp(48))
        back.bind(on_release=lambda *_: self.back())
        top.add_widget(back)
        top.add_widget(Title(text="معاينة بطاقة الطالب"))
        root.add_widget(top)

        self.preview_box = FloatLayout()
        self.preview_box.size_hint_y = 1
        root.add_widget(self.preview_box)

        actions = BoxLayout(size_hint_y=None, height=dp(58), padding=dp(8), spacing=dp(8))
        save = AppButton(text="حفظ البطاقة")
        save.bind(on_release=lambda *_: self.save_card())
        actions.add_widget(save)
        root.add_widget(actions)
        self.add_widget(root)
        self.student = None

    def load_student(self, s):
        self.student = s
        self.preview_box.clear_widgets()
        img = Image(source=TEMPLATE, allow_stretch=True, keep_ratio=False)
        img.size_hint = (0.96, 0.80)
        img.pos_hint = {"center_x": .5, "center_y": .52}
        self.preview_box.add_widget(img)

        # Overlay approximate fields matching the supplied card design.
        vals = [
            (s[2], .75, .735, "16sp"),
            (s[3] or "", .75, .655, "15sp"),
            (s[4] or "", .75, .575, "15sp"),
            (s[5] or "", .75, .495, "15sp"),
        ]
        for text, x, y, fs in vals:
            lab = Label(text=text, color=NAVY, bold=True, font_size=fs,
                        halign="right", valign="middle", size_hint=(.45,.055),
                        pos_hint={"center_x":x, "center_y":y})
            self.preview_box.add_widget(lab)

        if s[7] and os.path.exists(s[7]):
            photo = Image(source=s[7], allow_stretch=True, keep_ratio=True,
                          size_hint=(.20,.29), pos_hint={"x":.085,"center_y":.57})
            self.preview_box.add_widget(photo)

    def back(self):
        self.manager.current = "student_form"

    def save_card(self):
        # Final image/PDF export is intentionally kept as the next production step.
        Popup(title="معاينة",
              content=Label(text="تم تجهيز المعاينة.\nإصدار PDF/طباعة البطاقة يمكن ربطه بزر التصدير في النسخة النهائية."),
              size_hint=(.9,.35)).open()

class RootManager(ScreenManager):
    pass

class StudentCardApp(App):
    def build(self):
        Window.clearcolor = LIGHT
        init_db()
        sm = RootManager(transition=SlideTransition(duration=.18))
        sm.add_widget(Dashboard(name="dashboard"))
        sm.add_widget(Students(name="students"))
        sm.add_widget(StudentForm(name="student_form"))
        sm.add_widget(Preview(name="preview"))
        return sm

if __name__ == "__main__":
    StudentCardApp().run()
