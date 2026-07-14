# appModules/bruno.py
# NVDA add-on for Bruno API Client

import appModuleHandler
import controlTypes
import queueHandler
import speech
import textInfos
from NVDAObjects import NVDAObject

_TAG_TEXTAREA    = "textarea"
_CLASS_MOUSETRAP = "mousetrap"
_APP_NAME        = "bruno"
_MEMORY_LIMIT    = 50  # max tracked fields; oldest pruned when exceeded


def _say(text):
	if not text:
		return
	speech.cancelSpeech()
	queueHandler.queueFunction(queueHandler.eventQueue, speech.speakMessage, text)

def _say_char(ch):
	if not ch:
		return
	speech.cancelSpeech()
	queueHandler.queueFunction(queueHandler.eventQueue, speech.speakTypedCharacters, ch)
def _ia2_text(obj):
	try:
		return obj.makeTextInfo(textInfos.POSITION_ALL).text or ""
	except (AttributeError, RuntimeError, NotImplementedError):
		return ""

class BrunoMousetrapField(NVDAObject):
	@property
	def states(self):
		return super().states - {controlTypes.State.OFFSCREEN}

	def _key(self):
		try:
			a = self.IA2Attributes
			return f"{self.windowHandle}|{a.get('tag','')}|{a.get('text-input-type','')}"
		except AttributeError:
			return str(self.windowHandle)

	def _text(self):
		return self.appModule._memory.get(self._key(), "")

	def _cursor(self):
		return self.appModule._cursors.get(self._key(), 0)

	def _set_text(self, value):
		key = self._key()
		mem = self.appModule._memory
		if key not in mem and len(mem) >= _MEMORY_LIMIT:
			oldest = next(iter(mem))
			del mem[oldest]
			self.appModule._cursors.pop(oldest, None)
		mem[key] = value

	def _set_cursor(self, pos):
		self.appModule._cursors[self._key()] = max(0, min(pos, len(self._text())))

	def event_gainFocus(self):
		real = _ia2_text(self)
		if real:
			self._set_text(real)
			self._set_cursor(len(real))
			super().event_gainFocus()
			return

		text = self._text()
		self._set_cursor(len(text))

		super().event_gainFocus()
		_say(text or _("blank"))

	def event_typedCharacter(self, ch):
		if not ch or ord(ch) < 32 or 0xD800 <= ord(ch) <= 0xDFFF:
			return
		text, cursor = self._text(), self._cursor()
		self._set_text(text[:cursor] + ch + text[cursor:])
		self._set_cursor(cursor + 1)
		_say_char(ch)

	def _delete_char(self, gesture, offset):
		text, cursor = self._text(), self._cursor()
		target = cursor + offset
		if text and 0 <= target < len(text):
			ch = text[target]
			self._set_text(text[:target] + text[target + 1:])
			self._set_cursor(target)
			gesture.send()
			_say_char(ch)
		else:
			gesture.send()

	def script_deletePreviousCharacter(self, gesture):
		self._delete_char(gesture, -1)

	def script_deleteNextCharacter(self, gesture):
		self._delete_char(gesture, 0)

	def _move_caret(self, gesture, direction):
		text, cursor = self._text(), self._cursor()
		gesture.send()
		new = cursor + direction
		if 0 <= new < len(text):
			self._set_cursor(new)
			ch = text[cursor] if direction == 1 else text[new]
			_say_char(ch)
		elif new == len(text):
			self._set_cursor(new)

	def script_moveCaretRight(self, gesture):
		self._move_caret(gesture, 1)

	def script_moveCaretLeft(self, gesture):
		self._move_caret(gesture, -1)

	def script_moveCaretEnd(self, gesture):
		self._set_cursor(len(self._text()))
		gesture.send()

	def script_moveCaretHome(self, gesture):
		self._set_cursor(0)
		gesture.send()

	__gestures = {
		"kb:backspace":  "deletePreviousCharacter",
		"kb:delete":     "deleteNextCharacter",
		"kb:rightArrow": "moveCaretRight",
		"kb:leftArrow":  "moveCaretLeft",
		"kb:end":        "moveCaretEnd",
		"kb:home":       "moveCaretHome",
	}

class AppModule(appModuleHandler.AppModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._memory  = {}
		self._cursors = {}

	def terminate(self):
		self._memory.clear()
		self._cursors.clear()
		super().terminate()

	@staticmethod
	def _is_mousetrap(obj):
		try:
			if obj.role != controlTypes.Role.EDITABLETEXT:
				return False
			if controlTypes.State.EDITABLE not in obj.states:
				return False
			attrs = obj.IA2Attributes
			if attrs.get("tag") != _TAG_TEXTAREA:
				return False
			if _CLASS_MOUSETRAP not in attrs.get("class", ""):
				return False
			return not _ia2_text(obj)
		except AttributeError:
			return False

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		try:
			if obj.appModule.appName.lower() != _APP_NAME:
				return
		except AttributeError:
			return
		if self._is_mousetrap(obj):
			clsList.insert(0, BrunoMousetrapField)
