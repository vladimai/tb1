#!/usr/bin/env python3

import cachetools.func
import asyncio
import io
import tempfile
import traceback

import edge_tts

import utils
import my_log


VOICES = {
    'af': {'male': 'af-ZA-WillemNeural', 'female': 'af-ZA-AdriNeural'},
    'am': {'male': 'am-ET-AmehaNeural', 'female': 'am-ET-MekdesNeural'},
    'ar': {'male': 'ar-AE-HamdanNeural', 'female': 'ar-AE-FatimaNeural'},
    'ar2': {'male': 'ar-BH-AliNeural', 'female': 'ar-BH-LailaNeural'},
    'ar3': {'male': 'ar-DZ-IsmaelNeural', 'female': 'ar-DZ-AminaNeural'},
    'ar4': {'male': 'ar-EG-ShakirNeural', 'female': 'ar-EG-SalmaNeural'},
    'ar5': {'male': 'ar-IQ-BasselNeural', 'female': 'ar-IQ-RanaNeural'},
    'ar6': {'male': 'ar-JO-TaimNeural', 'female': 'ar-JO-SanaNeural'},
    'ar7': {'male': 'ar-KW-FahedNeural', 'female': 'ar-KW-NouraNeural'},
    'ar8': {'male': 'ar-LB-RamiNeural', 'female': 'ar-LB-LaylaNeural'},
    'ar9': {'male': 'ar-LY-OmarNeural', 'female': 'ar-LY-ImanNeural'},
    'ar10': {'male': 'ar-MA-JamalNeural', 'female': 'ar-MA-MounaNeural'},
    'ar11': {'male': 'ar-OM-AbdullahNeural', 'female': 'ar-OM-AyshaNeural'},
    'ar12': {'male': 'ar-QA-MoazNeural', 'female': 'ar-QA-AmalNeural'},
    'ar13': {'male': 'ar-SA-HamedNeural', 'female': 'ar-SA-ZariyahNeural'},
    'ar14': {'male': 'ar-SY-LaithNeural', 'female': 'ar-SY-AmanyNeural'},
    'ar15': {'male': 'ar-TN-HediNeural', 'female': 'ar-TN-ReemNeural'},
    'ar16': {'male': 'ar-YE-SalehNeural', 'female': 'ar-YE-MaryamNeural'},
    'az': {'male': 'az-AZ-BabekNeural', 'female': 'az-AZ-BanuNeural'},
    'bg': {'male': 'bg-BG-BorislavNeural', 'female': 'bg-BG-KalinaNeural'},
    'bn': {'male': 'bn-BD-PradeepNeural', 'female': 'bn-BD-NabanitaNeural'},
    'bn2': {'male': 'bn-IN-BashkarNeural', 'female': 'bn-IN-TanishaaNeural'},
    'bs': {'male': 'bs-BA-GoranNeural', 'female': 'bs-BA-VesnaNeural'},
    'ca': {'male': 'ca-ES-EnricNeural', 'female': 'ca-ES-JoanaNeural'},
    'cs': {'male': 'cs-CZ-AntoninNeural', 'female': 'cs-CZ-VlastaNeural'},
    'cy': {'male': 'cy-GB-AledNeural', 'female': 'cy-GB-NiaNeural'},
    'da': {'male': 'da-DK-JeppeNeural', 'female': 'da-DK-ChristelNeural'},
    'de': {'male': 'de-DE-FlorianMultilingualNeural', 'female': 'de-DE-SeraphinaMultilingualNeural'},
    'de2': {'male': 'de-AT-JonasNeural', 'female': 'de-AT-IngridNeural'},
    'de3': {'male': 'de-CH-JanNeural', 'female': 'de-CH-LeniNeural'},
    'de4': {'male': 'de-DE-ConradNeural', 'female': 'de-DE-AmalaNeural'},
    'de5': {'male': 'de-DE-KillianNeural', 'female': 'de-DE-KatjaNeural'},
    'el': {'male': 'el-GR-NestorasNeural', 'female': 'el-GR-AthinaNeural'},
    'en': {'male': 'en-US-AndrewMultilingualNeural', 'female': 'en-US-AvaMultilingualNeural'},
    'en2': {'male': 'en-US-BrianMultilingualNeural', 'female': 'en-US-EmmaMultilingualNeural'},
    'en3': {'male': 'en-AU-WilliamNeural', 'female': 'en-AU-NatashaNeural'},
    'en4': {'male': 'en-CA-LiamNeural', 'female': 'en-CA-ClaraNeural'},
    'en5': {'male': 'en-GB-RyanNeural', 'female': 'en-GB-LibbyNeural'},
    'en6': {'male': 'en-GB-ThomasNeural', 'female': 'en-GB-MaisieNeural'},
    'en7': {'male': None, 'female': 'en-GB-SoniaNeural'},
    'en8': {'male': 'en-HK-SamNeural', 'female': 'en-HK-YanNeural'},
    'en9': {'male': 'en-IE-ConnorNeural', 'female': 'en-IE-EmilyNeural'},
    'en10': {'male': 'en-IN-PrabhatNeural', 'female': 'en-IN-NeerjaExpressiveNeural'},
    'en11': {'male': None, 'female': 'en-IN-NeerjaNeural'},
    'en12': {'male': 'en-KE-ChilembaNeural', 'female': 'en-KE-AsiliaNeural'},
    'en13': {'male': 'en-NG-AbeoNeural', 'female': 'en-NG-EzinneNeural'},
    'en14': {'male': 'en-NZ-MitchellNeural', 'female': 'en-NZ-MollyNeural'},
    'en15': {'male': 'en-PH-JamesNeural', 'female': 'en-PH-RosaNeural'},
    'en16': {'male': 'en-SG-WayneNeural', 'female': 'en-SG-LunaNeural'},
    'en17': {'male': 'en-TZ-ElimuNeural', 'female': 'en-TZ-ImaniNeural'},
    'en18': {'male': 'en-US-AndrewNeural', 'female': 'en-US-AnaNeural'},
    'en19': {'male': 'en-US-BrianNeural', 'female': 'en-US-AriaNeural'},
    'en20': {'male': 'en-US-ChristopherNeural', 'female': 'en-US-AvaNeural'},
    'en21': {'male': 'en-US-EricNeural', 'female': 'en-US-EmmaNeural'},
    'en22': {'male': 'en-US-GuyNeural', 'female': 'en-US-JennyNeural'},
    'en23': {'male': 'en-US-RogerNeural', 'female': 'en-US-MichelleNeural'},
    'en24': {'male': 'en-US-SteffanNeural', 'female': None},
    'en25': {'male': 'en-ZA-LukeNeural', 'female': 'en-ZA-LeahNeural'},
    'es': {'male': 'es-AR-TomasNeural', 'female': 'es-AR-ElenaNeural'},
    'es2': {'male': 'es-BO-MarceloNeural', 'female': 'es-BO-SofiaNeural'},
    'es3': {'male': 'es-CL-LorenzoNeural', 'female': 'es-CL-CatalinaNeural'},
    'es4': {'male': 'es-CO-GonzaloNeural', 'female': 'es-CO-SalomeNeural'},
    'es5': {'male': 'es-CR-JuanNeural', 'female': 'es-CR-MariaNeural'},
    'es6': {'male': 'es-CU-ManuelNeural', 'female': 'es-CU-BelkysNeural'},
    'es7': {'male': 'es-DO-EmilioNeural', 'female': 'es-DO-RamonaNeural'},
    'es8': {'male': 'es-EC-LuisNeural', 'female': 'es-EC-AndreaNeural'},
    'es9': {'male': 'es-ES-AlvaroNeural', 'female': 'es-ES-ElviraNeural'},
    'es10': {'male': None, 'female': 'es-ES-XimenaNeural'},
    'es11': {'male': 'es-GQ-JavierNeural', 'female': 'es-GQ-TeresaNeural'},
    'es12': {'male': 'es-GT-AndresNeural', 'female': 'es-GT-MartaNeural'},
    'es13': {'male': 'es-HN-CarlosNeural', 'female': 'es-HN-KarlaNeural'},
    'es14': {'male': 'es-MX-JorgeNeural', 'female': 'es-MX-DaliaNeural'},
    'es15': {'male': 'es-NI-FedericoNeural', 'female': 'es-NI-YolandaNeural'},
    'es16': {'male': 'es-PA-RobertoNeural', 'female': 'es-PA-MargaritaNeural'},
    'es17': {'male': 'es-PE-AlexNeural', 'female': 'es-PE-CamilaNeural'},
    'es18': {'male': 'es-PR-VictorNeural', 'female': 'es-PR-KarinaNeural'},
    'es19': {'male': 'es-PY-MarioNeural', 'female': 'es-PY-TaniaNeural'},
    'es20': {'male': 'es-SV-RodrigoNeural', 'female': 'es-SV-LorenaNeural'},
    'es21': {'male': 'es-US-AlonsoNeural', 'female': 'es-US-PalomaNeural'},
    'es22': {'male': 'es-UY-MateoNeural', 'female': 'es-UY-ValentinaNeural'},
    'es23': {'male': 'es-VE-SebastianNeural', 'female': 'es-VE-PaolaNeural'},
    'et': {'male': 'et-EE-KertNeural', 'female': 'et-EE-AnuNeural'},
    'fa': {'male': 'fa-IR-FaridNeural', 'female': 'fa-IR-DilaraNeural'},
    'fi': {'male': 'fi-FI-HarriNeural', 'female': 'fi-FI-NooraNeural'},
    'fil': {'male': 'fil-PH-AngeloNeural', 'female': 'fil-PH-BlessicaNeural'},
    'fr': {'male': 'fr-FR-RemyMultilingualNeural', 'female': 'fr-FR-VivienneMultilingualNeural'},
    'fr2': {'male': 'fr-BE-GerardNeural', 'female': 'fr-BE-CharlineNeural'},
    'fr3': {'male': 'fr-CA-AntoineNeural', 'female': 'fr-CA-SylvieNeural'},
    'fr4': {'male': 'fr-CA-JeanNeural', 'female': None},
    'fr5': {'male': 'fr-CA-ThierryNeural', 'female': None},
    'fr6': {'male': 'fr-CH-FabriceNeural', 'female': 'fr-CH-ArianeNeural'},
    'fr7': {'male': 'fr-FR-HenriNeural', 'female': 'fr-FR-DeniseNeural'},
    'fr8': {'male': None, 'female': 'fr-FR-EloiseNeural'},
    'ga': {'male': 'ga-IE-ColmNeural', 'female': 'ga-IE-OrlaNeural'},
    'gl': {'male': 'gl-ES-RoiNeural', 'female': 'gl-ES-SabelaNeural'},
    'gu': {'male': 'gu-IN-NiranjanNeural', 'female': 'gu-IN-DhwaniNeural'},
    'he': {'male': 'he-IL-AvriNeural', 'female': 'he-IL-HilaNeural'},
    'hi': {'male': 'hi-IN-MadhurNeural', 'female': 'hi-IN-SwaraNeural'},
    'hr': {'male': 'hr-HR-SreckoNeural', 'female': 'hr-HR-GabrijelaNeural'},
    'hu': {'male': 'hu-HU-TamasNeural', 'female': 'hu-HU-NoemiNeural'},
    'id': {'male': 'id-ID-ArdiNeural', 'female': 'id-ID-GadisNeural'},
    'is': {'male': 'is-IS-GunnarNeural', 'female': 'is-IS-GudrunNeural'},
    'it': {'male': 'it-IT-DiegoNeural', 'female': 'it-IT-ElsaNeural'},
    'it2': {'male': 'it-IT-GiuseppeNeural', 'female': 'it-IT-IsabellaNeural'},
    'ja': {'male': 'ja-JP-KeitaNeural', 'female': 'ja-JP-NanamiNeural'},
    'jv': {'male': 'jv-ID-DimasNeural', 'female': 'jv-ID-SitiNeural'},
    'ka': {'male': 'ka-GE-GiorgiNeural', 'female': 'ka-GE-EkaNeural'},
    'kk': {'male': 'kk-KZ-DauletNeural', 'female': 'kk-KZ-AigulNeural'},
    'km': {'male': 'km-KH-PisethNeural', 'female': 'km-KH-SreymomNeural'},
    'kn': {'male': 'kn-IN-GaganNeural', 'female': 'kn-IN-SapnaNeural'},
    'ko': {'male': 'ko-KR-HyunsuNeural', 'female': 'ko-KR-SunHiNeural'},
    'ko2': {'male': 'ko-KR-InJoonNeural', 'female': None},
    'lo': {'male': 'lo-LA-ChanthavongNeural', 'female': 'lo-LA-KeomanyNeural'},
    'lt': {'male': 'lt-LT-LeonasNeural', 'female': 'lt-LT-OnaNeural'},
    'lv': {'male': 'lv-LV-NilsNeural', 'female': 'lv-LV-EveritaNeural'},
    'mk': {'male': 'mk-MK-AleksandarNeural', 'female': 'mk-MK-MarijaNeural'},
    'ml': {'male': 'ml-IN-MidhunNeural', 'female': 'ml-IN-SobhanaNeural'},
    'mn': {'male': 'mn-MN-BataaNeural', 'female': 'mn-MN-YesuiNeural'},
    'mr': {'male': 'mr-IN-ManoharNeural', 'female': 'mr-IN-AarohiNeural'},
    'ms': {'male': 'ms-MY-OsmanNeural', 'female': 'ms-MY-YasminNeural'},
    'mt': {'male': 'mt-MT-JosephNeural', 'female': 'mt-MT-GraceNeural'},
    'my': {'male': 'my-MM-ThihaNeural', 'female': 'my-MM-NilarNeural'},
    'nb': {'male': 'nb-NO-FinnNeural', 'female': 'nb-NO-PernilleNeural'},
    'ne': {'male': 'ne-NP-SagarNeural', 'female': 'ne-NP-HemkalaNeural'},
    'nl': {'male': 'nl-BE-ArnaudNeural', 'female': 'nl-BE-DenaNeural'},
    'nl2': {'male': 'nl-NL-MaartenNeural', 'female': 'nl-NL-ColetteNeural'},
    'nl3': {'male': None, 'female': 'nl-NL-FennaNeural'},
    'pl': {'male': 'pl-PL-MarekNeural', 'female': 'pl-PL-ZofiaNeural'},
    'ps': {'male': 'ps-AF-GulNawazNeural', 'female': 'ps-AF-LatifaNeural'},
    'pt': {'male': 'pt-BR-AntonioNeural', 'female': 'pt-BR-FranciscaNeural'},
    'pt2': {'male': None, 'female': 'pt-BR-ThalitaNeural'},
    'pt3': {'male': 'pt-PT-DuarteNeural', 'female': 'pt-PT-RaquelNeural'},
    'ro': {'male': 'ro-RO-EmilNeural', 'female': 'ro-RO-AlinaNeural'},
    'ru': {'male': 'ru-RU-DmitryNeural', 'female': 'ru-RU-SvetlanaNeural'},
    'si': {'male': 'si-LK-SameeraNeural', 'female': 'si-LK-ThiliniNeural'},
    'sk': {'male': 'sk-SK-LukasNeural', 'female': 'sk-SK-ViktoriaNeural'},
    'sl': {'male': 'sl-SI-RokNeural', 'female': 'sl-SI-PetraNeural'},
    'so': {'male': 'so-SO-MuuseNeural', 'female': 'so-SO-UbaxNeural'},
    'sq': {'male': 'sq-AL-IlirNeural', 'female': 'sq-AL-AnilaNeural'},
    'sr': {'male': 'sr-RS-NicholasNeural', 'female': 'sr-RS-SophieNeural'},
    'su': {'male': 'su-ID-JajangNeural', 'female': 'su-ID-TutiNeural'},
    'sv': {'male': 'sv-SE-MattiasNeural', 'female': 'sv-SE-SofieNeural'},
    'sw': {'male': 'sw-KE-RafikiNeural', 'female': 'sw-KE-ZuriNeural'},
    'sw2': {'male': 'sw-TZ-DaudiNeural', 'female': 'sw-TZ-RehemaNeural'},
    'ta': {'male': 'ta-IN-ValluvarNeural', 'female': 'ta-IN-PallaviNeural'},
    'ta2': {'male': 'ta-LK-KumarNeural', 'female': 'ta-LK-SaranyaNeural'},
    'ta3': {'male': 'ta-MY-SuryaNeural', 'female': 'ta-MY-KaniNeural'},
    'ta4': {'male': 'ta-SG-AnbuNeural', 'female': 'ta-SG-VenbaNeural'},
    'te': {'male': 'te-IN-MohanNeural', 'female': 'te-IN-ShrutiNeural'},
    'th': {'male': 'th-TH-NiwatNeural', 'female': 'th-TH-PremwadeeNeural'},
    'tr': {'male': 'tr-TR-AhmetNeural', 'female': 'tr-TR-EmelNeural'},
    'uk': {'male': 'uk-UA-OstapNeural', 'female': 'uk-UA-PolinaNeural'},
    'ur': {'male': 'ur-IN-SalmanNeural', 'female': 'ur-IN-GulNeural'},
    'ur2': {'male': 'ur-PK-AsadNeural', 'female': 'ur-PK-UzmaNeural'},
    'uz': {'male': 'uz-UZ-SardorNeural', 'female': 'uz-UZ-MadinaNeural'},
    'vi': {'male': 'vi-VN-NamMinhNeural', 'female': 'vi-VN-HoaiMyNeural'},
    'zh': {'male': 'zh-CN-YunjianNeural', 'female': 'zh-CN-XiaoxiaoNeural'},
    'zh2': {'male': 'zh-CN-YunxiNeural', 'female': 'zh-CN-XiaoyiNeural'},
    'zh3': {'male': 'zh-CN-YunxiaNeural', 'female': 'zh-CN-liaoning-XiaobeiNeural'},
    'zh4': {'male': 'zh-CN-YunyangNeural', 'female': 'zh-CN-shaanxi-XiaoniNeural'},
    'zh5': {'male': 'zh-HK-WanLungNeural', 'female': 'zh-HK-HiuGaaiNeural'},
    'zh6': {'male': None, 'female': 'zh-HK-HiuMaanNeural'},
    'zh7': {'male': 'zh-TW-YunJheNeural', 'female': 'zh-TW-HsiaoChenNeural'},
    'zh8': {'male': None, 'female': 'zh-TW-HsiaoYuNeural'},
    'zu': {'male': 'zu-ZA-ThembaNeural', 'female': 'zu-ZA-ThandoNeural'},
}


def get_voice(language_code: str, gender: str = 'female'):
    """принимает двухбуквенное обозначение языка и возвращает голосовой движок для его озвучки
    gender = 'male' or 'female'"""
    
    assert gender in ('male', 'female')

    # белорусский язык это скорее всего ошибка автоопределителя, но в любом случае такой язык не поддерживается, меняем на украинский
    if language_code == 'be':
        language_code = 'uk'

    if language_code == 'ua':
        language_code = 'uk'
    return VOICES[language_code][gender] or ''


@cachetools.func.ttl_cache(maxsize=10, ttl=10 * 60)
def tts(text: str, voice: str = 'ru', rate: str = '+0%', gender: str = 'female') -> bytes:
    """
    Generates text-to-speech audio from the given input text using the specified voice, 
    speech rate, and gender.

    Args:
        text (str): The input text to convert to speech.
        voice (str, optional): The voice to use for the speech. Defaults to 'ru'.
        rate (str, optional): The speech rate. Defaults to '+0%'.
        gender (str, optional): The gender of the voice. Defaults to 'female'.

    Returns:
        bytes: The generated audio as a bytes object.
    """
    try:
        lang = voice

        voice = get_voice(voice, gender)

        print('tts: ', text, voice, rate, gender)

        # Удаляем символы переноса строки и перевода каретки 
        text = text.replace('\r','')
        text = text.replace('\n\n','\n')
        # заменить ! на точку, с восклицательным знаком очень плохие переходы получаются
        if lang == 'ru':
            text = text.replace('!', '.')

        print('tts: ', text, voice, rate, gender)

        # Создаем временный файл для записи аудио
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as f: 
            filename = f.name 

        # Запускаем edge-tts для генерации аудио
        com = edge_tts.Communicate(text, voice, rate=rate)

        asyncio.run(com.save(filename))

        # Читаем аудио из временного файла 
        with open(filename, "rb") as f: 
            data = io.BytesIO(f.read())

        utils.remove_file(filename)

        # Возвращаем байтовый поток с аудио
        data = data.getvalue()

        print('tts: data len ', len(data))

        if data:
            return data
        return b''
    except edge_tts.exceptions.NoAudioReceived:
        return b''
    except Exception as error:
        error_traceback = traceback.format_exc()
        my_log.log2(f'my_tts:tts: {error}\n\n{error_traceback}')
        return b''


if __name__ == "__main__":
    pass
