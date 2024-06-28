#!/usr/bin/env python3

import cachetools.func
import asyncio
import io
import glob
import os
import tempfile
import traceback

import edge_tts
import gtts

import utils
import my_log


VOICES = {
    'af' :  {'male': 'af-ZA-WillemNeural', 'female': 'af-ZA-AdriNeural'},
    'am' :  {'male': 'am-ET-AmehaNeural', 'female': 'am-ET-MekdesNeural'},
    'ar' :  {'male': 'ar-AE-HamdanNeural', 'female': 'ar-AE-FatimaNeural'},
    'ar2' :  {'male': 'ar-BH-AliNeural', 'female': 'ar-BH-LailaNeural'},
    'ar3' :  {'male': 'ar-DZ-IsmaelNeural', 'female': 'ar-DZ-AminaNeural'},
    'ar4' :  {'male': 'ar-EG-ShakirNeural', 'female': 'ar-EG-SalmaNeural'},
    'ar5' :  {'male': 'ar-IQ-BasselNeural', 'female': 'ar-IQ-RanaNeural'},
    'ar6' :  {'male': 'ar-JO-TaimNeural', 'female': 'ar-JO-SanaNeural'},
    'ar7' :  {'male': 'ar-KW-FahedNeural', 'female': 'ar-KW-NouraNeural'},
    'ar8' :  {'male': 'ar-LB-RamiNeural', 'female': 'ar-LB-LaylaNeural'},
    'ar9' :  {'male': 'ar-LY-OmarNeural', 'female': 'ar-LY-ImanNeural'},
    'ar10' :  {'male': 'ar-MA-JamalNeural', 'female': 'ar-MA-MounaNeural'},
    'ar11' :  {'male': 'ar-OM-AbdullahNeural', 'female': 'ar-OM-AyshaNeural'},
    'ar12' :  {'male': 'ar-QA-MoazNeural', 'female': 'ar-QA-AmalNeural'},
    'ar13' :  {'male': 'ar-SA-HamedNeural', 'female': 'ar-SA-ZariyahNeural'},
    'ar14' :  {'male': 'ar-SY-LaithNeural', 'female': 'ar-SY-AmanyNeural'},
    'ar15' :  {'male': 'ar-TN-HediNeural', 'female': 'ar-TN-ReemNeural'},
    'ar16' :  {'male': 'ar-YE-SalehNeural', 'female': 'ar-YE-MaryamNeural'},
    'az' :  {'male': 'az-AZ-BabekNeural', 'female': 'az-AZ-BanuNeural'},
    'bg' :  {'male': 'bg-BG-BorislavNeural', 'female': 'bg-BG-KalinaNeural'},
    'bn' :  {'male': 'bn-BD-PradeepNeural', 'female': 'bn-BD-NabanitaNeural'},
    'bn2' :  {'male': 'bn-IN-BashkarNeural', 'female': 'bn-IN-TanishaaNeural'},
    'bs' :  {'male': 'bs-BA-GoranNeural', 'female': 'bs-BA-VesnaNeural'},
    'ca' :  {'male': 'ca-ES-EnricNeural', 'female': 'ca-ES-JoanaNeural'},
    'cs' :  {'male': 'cs-CZ-AntoninNeural', 'female': 'cs-CZ-VlastaNeural'},
    'cy' :  {'male': 'cy-GB-AledNeural', 'female': 'cy-GB-NiaNeural'},
    'da' :  {'male': 'da-DK-JeppeNeural', 'female': 'da-DK-ChristelNeural'},

    'de' :   {'male': 'de-DE-FlorianMultilingualNeural', 'female': 'de-DE-SeraphinaMultilingualNeural'},
    'de2' :  {'male': 'de-AT-JonasNeural', 'female': 'de-AT-IngridNeural'},
    'de3' :  {'male': 'de-CH-JanNeural', 'female': 'de-CH-LeniNeural'},
    'de4' :  {'male': 'de-DE-ConradNeural', 'female': 'de-DE-AmalaNeural'},
    'de5' :  {'male': 'de-DE-KillianNeural', 'female': 'de-DE-KatjaNeural'},

    'el' :  {'male': 'el-GR-NestorasNeural', 'female': 'el-GR-AthinaNeural'},

    'en' :    {'male': 'en-US-AndrewMultilingualNeural', 'female': 'en-US-EmmaMultilingualNeural'},
    'en2' :   {'male': 'en-CA-LiamNeural', 'female': 'en-CA-ClaraNeural'},
    'en3' :   {'male': 'en-GB-ThomasNeural', 'female': 'en-GB-MaisieNeural'},
    'en4' :   {'male': 'en-GB-RyanNeural', 'female': 'en-GB-SoniaNeural'},
    'en5' :   {'male': 'en-HK-SamNeural', 'female': 'en-IN-NeerjaExpressiveNeural'},
    'en6' :   {'male': 'en-IE-ConnorNeural', 'female': 'en-HK-YanNeural'},
    'en8' :   {'male': 'en-IN-PrabhatNeural', 'female': 'en-IN-NeerjaNeural'},
    'en9' :   {'male': 'en-KE-ChilembaNeural', 'female': 'en-KE-AsiliaNeural'},
    'en10' :  {'male': 'en-NG-AbeoNeural', 'female': 'en-NG-EzinneNeural'},
    'en11' :  {'male': 'en-NZ-MitchellNeural', 'female': 'en-NZ-MollyNeural'},
    'en12' :  {'male': 'en-PH-JamesNeural', 'female': 'en-PH-RosaNeural'},
    'en13' :  {'male': 'en-SG-WayneNeural', 'female': 'en-SG-LunaNeural'},
    'en14' :  {'male': 'en-TZ-ElimuNeural', 'female': 'en-TZ-ImaniNeural'},
    'en15' :  {'male': 'en-US-AndrewNeural', 'female': 'en-US-AriaNeural'},
    'en16' :  {'male': 'en-AU-WilliamNeural', 'female': 'en-AU-NatashaNeural'},
    'en17' :  {'male': 'en-US-BrianNeural', 'female': 'en-US-AvaNeural'},
    'en18' :  {'male': 'en-US-ChristopherNeural', 'female': 'en-US-AnaNeural'},
    'en19' :  {'male': 'en-US-EricNeural', 'female': 'en-US-EmmaNeural'},
    'en20' :  {'male': 'en-US-GuyNeural', 'female': 'en-US-JennyNeural'},
    'en21' :  {'male': 'en-US-RogerNeural', 'female': 'en-US-MichelleNeural'},
    'en22' :  {'male': 'en-ZA-LukeNeural', 'female': 'en-ZA-LeahNeural'},

    'es' :    {'male': 'es-BO-MarceloNeural', 'female': 'es-AR-ElenaNeural'},
    'es2' :   {'male': 'es-CO-GonzaloNeural', 'female': 'es-CL-CatalinaNeural'},
    'es3' :   {'male': 'es-CR-JuanNeural', 'female': 'es-CO-SalomeNeural'},
    'es4' :   {'male': 'es-DO-EmilioNeural', 'female': 'es-CU-BelkysNeural'},
    'es5' :   {'male': 'es-ES-AlvaroNeural', 'female': 'es-ES-XimenaNeural'},
    'es6' :   {'male': 'es-EC-LuisNeural', 'female': 'es-EC-AndreaNeural'},
    'es7' :   {'male': 'es-GQ-JavierNeural', 'female': 'es-GQ-TeresaNeural'},
    'es8' :   {'male': 'es-GT-AndresNeural', 'female': 'es-GT-MartaNeural'},
    'es9' :   {'male': 'es-HN-CarlosNeural', 'female': 'es-HN-KarlaNeural'},
    'es10' :  {'male': 'es-MX-JorgeNeural', 'female': 'es-MX-DaliaNeural'},
    'es11' :  {'male': 'es-NI-FedericoNeural', 'female': 'es-NI-YolandaNeural'},
    'es12' :  {'male': 'es-PA-RobertoNeural', 'female': 'es-PA-MargaritaNeural'},
    'es13' :  {'male': 'es-PE-AlexNeural', 'female': 'es-PE-CamilaNeural'},
    'es14' :  {'male': 'es-PR-VictorNeural', 'female': 'es-PR-KarinaNeural'},
    'es15' :  {'male': 'es-PY-MarioNeural', 'female': 'es-PY-TaniaNeural'},
    'es16' :  {'male': 'es-SV-RodrigoNeural', 'female': 'es-SV-LorenaNeural'},
    'es17' :  {'male': 'es-US-AlonsoNeural', 'female': 'es-US-PalomaNeural'},
    'es18' :  {'male': 'es-UY-MateoNeural', 'female': 'es-UY-ValentinaNeural'},
    'es19' :  {'male': 'es-VE-SebastianNeural', 'female': 'es-VE-PaolaNeural'},

    'et' :  {'male': 'et-EE-KertNeural', 'female': 'et-EE-AnuNeural'},
    'fa' :  {'male': 'fa-IR-FaridNeural', 'female': 'fa-IR-DilaraNeural'},
    'fi' :  {'male': 'fi-FI-HarriNeural', 'female': 'fi-FI-NooraNeural'},
    'fi2' :  {'male': 'fil-PH-AngeloNeural', 'female': 'fil-PH-BlessicaNeural'},

    'fr' :   {'male': 'fr-FR-RemyMultilingualNeural', 'female': 'fr-FR-VivienneMultilingualNeural'},
    'fr2' :  {'male': 'fr-CA-JeanNeural', 'female': 'fr-CA-AntoineNeural'},
    'fr3' :  {'male': 'fr-CA-ThierryNeural', 'female': 'fr-CA-SylvieNeural'},
    'fr4' :  {'male': 'fr-CH-FabriceNeural', 'female': 'fr-CH-ArianeNeural'},
    'fr5' :  {'male': 'fr-BE-GerardNeural', 'female': 'fr-BE-CharlineNeural'},

    'ga' :  {'male': 'ga-IE-ColmNeural', 'female': 'ga-IE-OrlaNeural'},

    'gl' :  {'male': 'gl-ES-RoiNeural', 'female': 'gl-ES-SabelaNeural'},

    'gu' :  {'male': 'gu-IN-NiranjanNeural', 'female': 'gu-IN-DhwaniNeural'},

    'he' :  {'male': 'he-IL-AvriNeural', 'female': 'he-IL-HilaNeural'},

    'hi' :  {'male': 'hi-IN-MadhurNeural', 'female': 'hi-IN-SwaraNeural'},

    'hr' :  {'male': 'hr-HR-SreckoNeural', 'female': 'hr-HR-GabrijelaNeural'},

    'hu' :  {'male': 'hu-HU-TamasNeural', 'female': 'hu-HU-NoemiNeural'},

    'id' :  {'male': 'id-ID-ArdiNeural', 'female': 'id-ID-GadisNeural'},

    'is' :  {'male': 'is-IS-GunnarNeural', 'female': 'is-IS-GudrunNeural'},

    'it' :  {'male': 'it-IT-DiegoNeural', 'female': 'it-IT-IsabellaNeural'},
    'it2' :  {'male': 'it-IT-GiuseppeNeural', 'female': 'it-IT-ElsaNeural'},

    'ja' :  {'male': 'ja-JP-KeitaNeural', 'female': 'ja-JP-NanamiNeural'},

    'jv' :  {'male': 'jv-ID-DimasNeural', 'female': 'jv-ID-SitiNeural'},

    'ka' :  {'male': 'ka-GE-GiorgiNeural', 'female': 'ka-GE-EkaNeural'},

    'kk' :  {'male': 'kk-KZ-DauletNeural', 'female': 'kk-KZ-AigulNeural'},

    'km' :  {'male': 'km-KH-PisethNeural', 'female': 'km-KH-SreymomNeural'},

    'kn' :  {'male': 'kn-IN-GaganNeural', 'female': 'kn-IN-SapnaNeural'},

    'ko' :  {'male': 'ko-KR-HyunsuNeural', 'female': 'ko-KR-SunHiNeural'}, # female copied
    'ko2' :  {'male': 'ko-KR-InJoonNeural', 'female': 'ko-KR-SunHiNeural'},

    'lo' :  {'male': 'lo-LA-ChanthavongNeural', 'female': 'lo-LA-KeomanyNeural'},
    'lt' :  {'male': 'lt-LT-LeonasNeural', 'female': 'lt-LT-OnaNeural'},
    'lv' :  {'male': 'lv-LV-NilsNeural', 'female': 'lv-LV-EveritaNeural'},
    'mk' :  {'male': 'mk-MK-AleksandarNeural', 'female': 'mk-MK-MarijaNeural'},
    'ml' :  {'male': 'ml-IN-MidhunNeural', 'female': 'ml-IN-SobhanaNeural'},
    'mn' :  {'male': 'mn-MN-BataaNeural', 'female': 'mn-MN-YesuiNeural'},
    'mr' :  {'male': 'mr-IN-ManoharNeural', 'female': 'mr-IN-AarohiNeural'},
    'ms' :  {'male': 'ms-MY-OsmanNeural', 'female': 'ms-MY-YasminNeural'},
    'mt' :  {'male': 'mt-MT-JosephNeural', 'female': 'mt-MT-GraceNeural'},
    'my' :  {'male': 'my-MM-ThihaNeural', 'female': 'my-MM-NilarNeural'},
    'nb' :  {'male': 'nb-NO-FinnNeural', 'female': 'nb-NO-PernilleNeural'},
    'ne' :  {'male': 'ne-NP-SagarNeural', 'female': 'ne-NP-HemkalaNeural'},

    'nl' :   {'male': 'nl-BE-ArnaudNeural', 'female': 'nl-BE-DenaNeural'},
    'nl2' :  {'male': 'nl-NL-MaartenNeural', 'female': 'nl-NL-FennaNeural'},
    'nl3' :  {'male': 'nl-NL-MaartenNeural', 'female': 'nl-NL-ColetteNeural'}, # male copied

    'pl' :  {'male': 'pl-PL-MarekNeural', 'female': 'pl-PL-ZofiaNeural'},

    'ps' :  {'male': 'ps-AF-GulNawazNeural', 'female': 'ps-AF-LatifaNeural'},

    'pt' :  {'male': 'pt-BR-AntonioNeural', 'female': 'pt-BR-ThalitaNeural'},
    'pt2' :  {'male': 'pt-BR-AntonioNeural', 'female': 'pt-BR-FranciscaNeural'}, # male copied
    'pt3' :  {'male': 'pt-PT-DuarteNeural', 'female': 'pt-PT-RaquelNeural'},

    'ro' :  {'male': 'ro-RO-EmilNeural', 'female': 'ro-RO-AlinaNeural'},
    'ru' :  {'male': 'ru-RU-DmitryNeural', 'female': 'ru-RU-SvetlanaNeural'},
    'si' :  {'male': 'si-LK-SameeraNeural', 'female': 'si-LK-ThiliniNeural'},
    'sk' :  {'male': 'sk-SK-LukasNeural', 'female': 'sk-SK-ViktoriaNeural'},
    'sl' :  {'male': 'sl-SI-RokNeural', 'female': 'sl-SI-PetraNeural'},
    'so' :  {'male': 'so-SO-MuuseNeural', 'female': 'so-SO-UbaxNeural'},
    'sq' :  {'male': 'sq-AL-IlirNeural', 'female': 'sq-AL-AnilaNeural'},
    'sr' :  {'male': 'sr-RS-NicholasNeural', 'female': 'sr-RS-SophieNeural'},
    'su' :  {'male': 'su-ID-JajangNeural', 'female': 'su-ID-TutiNeural'},
    'sv' :  {'male': 'sv-SE-MattiasNeural', 'female': 'sv-SE-SofieNeural'},
    'sw' :  {'male': 'sw-KE-RafikiNeural', 'female': 'sw-KE-ZuriNeural'},
    'sw2' :  {'male': 'sw-TZ-DaudiNeural', 'female': 'sw-TZ-RehemaNeural'},
    'ta' :  {'male': 'ta-IN-ValluvarNeural', 'female': 'ta-IN-PallaviNeural'},
    'ta2' :  {'male': 'ta-LK-KumarNeural', 'female': 'ta-LK-SaranyaNeural'},
    'ta3' :  {'male': 'ta-MY-SuryaNeural', 'female': 'ta-MY-KaniNeural'},
    'ta4' :  {'male': 'ta-SG-AnbuNeural', 'female': 'ta-SG-VenbaNeural'},
    'te' :  {'male': 'te-IN-MohanNeural', 'female': 'te-IN-ShrutiNeural'},
    'th' :  {'male': 'th-TH-NiwatNeural', 'female': 'th-TH-PremwadeeNeural'},
    'tr' :  {'male': 'tr-TR-AhmetNeural', 'female': 'tr-TR-EmelNeural'},
    'uk' :  {'male': 'uk-UA-OstapNeural', 'female': 'uk-UA-PolinaNeural'},
    'ur' :  {'male': 'ur-IN-SalmanNeural', 'female': 'ur-IN-GulNeural'},
    'ur2' :  {'male': 'ur-PK-AsadNeural', 'female': 'ur-PK-UzmaNeural'},
    'uz' :  {'male': 'uz-UZ-SardorNeural', 'female': 'uz-UZ-MadinaNeural'},
    'vi' :  {'male': 'vi-VN-NamMinhNeural', 'female': 'vi-VN-HoaiMyNeural'},

    'zh': {'male': 'zh-CN-XiaoxiaoNeural', 'female': 'zh-CN-XiaoyiNeural'},
    'zh2': {'male': 'zh-CN-YunjianNeural', 'female': 'zh-CN-YunxiaNeural'},
    'zh3': {'male': 'zh-CN-YunyangNeural', 'female': 'zh-CN-liaoning-XiaobeiNeural'},
    'zh4': {'male': 'zh-CN-YunxiNeural', 'female': 'zh-CN-shaanxi-XiaoniNeural'},
    'zh5': {'male': 'zh-HK-HiuGaaiNeural', 'female': 'zh-HK-HiuMaanNeural'},
    'zh6': {'male': 'zh-HK-WanLungNeural', 'female': 'zh-HK-HiuGaaiNeural'},
    'zh7': {'male': 'zh-TW-YunJheNeural', 'female': 'zh-TW-HsiaoYuNeural'},
    'zh8': {'male': 'zh-TW-HsiaoChenNeural', 'female': 'zh-TW-YunJheNeural'},

    'zu' :  {'male': 'zu-ZA-ThembaNeural', 'female': 'zu-ZA-ThandoNeural'},
}


# cleanup
for filePath in [x for x in glob.glob('*.wav') + glob.glob('*.ogg') + glob.glob('*.mp4') + glob.glob('*.mp3') if 'temp_tts_file' in x]:
    try:
        utils.remove_file(filePath)
    except:
        print("Error while deleting file : ", filePath)


def tts_google(text: str, lang: str = 'ru', rate: str = '+0%') -> bytes:
    """
    Converts the given text to speech using the Google Text-to-Speech (gTTS) API.

    Parameters:
        text (str): The text to be converted to speech.
        lang (str, optional): The language of the text. Defaults to 'ru'.

    Returns:
        bytes: The generated audio as a bytes object.
    """
    if lang == 'en2':
        lang = 'en'
    mp3_fp = io.BytesIO()
    result = gtts.gTTS(text, lang=lang)
    result.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    data = mp3_fp.read()
    return data


def get_voice(language_code: str, gender: str = 'female'):
    """принимает двухбуквенное обозначение языка и возвращает голосовой движок для его озвучки
    gender = 'male' or 'female'"""
    
    assert gender in ('male', 'female')

    # белорусский язык это скорее всего ошибка автоопределителя, но в любом случае такой язык не поддерживается, меняем на украинский
    if language_code == 'be':
        language_code = 'uk'

    if language_code == 'ua':
        language_code = 'uk'
    return VOICES[language_code][gender]


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

        if gender == 'google_female':
            return tts_google(text, lang)

        voice = get_voice(voice, gender)

        # Удаляем символы переноса строки и перевода каретки 
        text = text.replace('\r','') 
        text = text.replace('\n\n','\n')  

        # Создаем временный файл для записи аудио
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as f: 
            filename = f.name 

        # Запускаем edge-tts для генерации аудио
        com = edge_tts.Communicate(text, voice, rate=rate)
        # com = edge_tts.Communicate(text, voice)
        asyncio.run(com.save(filename))

        # Читаем аудио из временного файла 
        with open(filename, "rb") as f: 
            data = io.BytesIO(f.read())

        utils.remove_file(filename)
        # Возвращаем байтовый поток с аудио
        data = data.getvalue()

        return data
    except edge_tts.exceptions.NoAudioReceived:
        return None
    except Exception as error:
        error_traceback = traceback.format_exc()
        my_log.log2(f'my_tts:tts: {error}\n\n{error_traceback}')
        return None


if __name__ == "__main__":
    # print(tts('привет', 'ja'))
    l = []
    for k in VOICES:
        if k not in l:
            l.append(k)
    print(l)
