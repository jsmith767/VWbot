from enum import Enum

class ChatGroups(Enum):
    MAIN = '-1001666785355'
    INFO = '-1001585977848'
    BOTDEV = '-1001810667392'
    ADMIN = '-1001810667392'

MATHEMATICAL_BOLD_SCRIPT = {'a': '𝓪', 'b': '𝓫', 'c': '𝓬', 'd': '𝓭', 'e': '𝓮', 'f': '𝓯', 'g': '𝓰', 'h': '𝓱', 'i': '𝓲', 'j': '𝓳', 'k': '𝓴', 'l': '𝓵', 'm': '𝓶', 'n': '𝓷', 'o': '𝓸', 'p': '𝓹', 'q': '𝓺', 'r': '𝓻', 's': '𝓼', 't': '𝓽', 'u': '𝓾', 'v': '𝓿', 'w': '𝔀', 'x': '𝔁', 'y': '𝔂', 'z': '𝔃', 'A': '𝓐', 'B': '𝓑', 'C': '𝓒', 'D': '𝓓', 'E': '𝓔', 'F': '𝓕', 'G': '𝓖', 'H': '𝓗', 'I': '𝓘', 'J': '𝓙', 'K': '𝓚', 'L': '𝓛', 'M': '𝓜', 'N': '𝓝', 'O': '𝓞', 'P': '𝓟', 'Q': '𝓠', 'R': '𝓡', 'S': '𝓢', 'T': '𝓣', 'U': '𝓤', 'V': '𝓥', 'W': '𝓦', 'X': '𝓧', 'Y': '𝓨', 'Z': '𝓩'}

class Font(Enum):
    '''Represents the starting position for a unicode character set'''
    LATIN = 65 #ord('A')
    NEGATIVE_SQUARED_LATIN = 127344 #ord('🅰')
    NEGATIVE_CIRCLED_LATIN = 127312 #ord('🅐')
    SQUARED_LATIN = 127280 #ord('🄰')
    REGIONAL_INDICATOR_SYMBOL = 127462 #ord('🇦')
    MATHEMATICAL_BOLD_SCRIPT = 120016 #ord('𝓐')
    LOWER_LATIN = 97 #ord('a')
    LOWER_MATHEMATICAL_DOUBLE_STRUCK = 120146 #ord('𝕒')
    LOWER_MATHEMATICAL_FRAKTUR = 120094 #ord('𝔞')
    LOWER_MATHEMATICAL_BOLD_SCRIPT = 120042 #ord('𝓪')
    LOWER_LATIN_LETTER_SMALL_CAP = 7424 #ord('ᴀ')

class Decoration(Enum):
    STAR_HR = '✦——————————✦'
    CAT_HR = '=^..^=   =^..^=   =^..^='
    BUBBLE_HR = '.oOo.oOo.oOo.oOo.oOo.'

class Emoticon(Enum):
    A = r'(¬_¬”)'
    B = r'(づ￣ ³￣)づ'
    C = r'(╥﹏╥)'
    D = r'(っ◔◡◔)っ ♥'
    E = r'(￣ω￣﻿)'
    F = r'{¬ºཀ°}¬'
    G = r'ʕ•ᴥ•ʔ'
    H = r'ヽ(ヅ)ノ'
    I = r'¯\_ಠ_ಠ_/¯'
    J = r'¯\(ツ)/¯'
    K = r'(≖ᴗ≖)'
    L = r'(◑_◑)'
    M = r'ಠಗಠ'
    N = r'd[ o_0 ]b'
    O = r'^⨀ᴥ⨀^'
    P = r'٩(̾●̮̮̃̾•̃̾)۶'
    Q = r'ˁ˚ᴥ˚ˀ'
    R = r'ʕʘ̅͜ʘ̅ʔ'
    T = r'(╯°□°）╯︵ ┻━┻'

class UserAccessLevel(Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    NONE = "NONE"

class ConfirmKBD(Enum):
    CONFIRM = 1
    CANCEL = 0