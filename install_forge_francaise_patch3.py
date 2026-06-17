from pathlib import Path
import subprocess
import textwrap
import json

ROOT = Path(r"D:\PYTHON\Forge Francaise")
REMOTE_URL = "https://github.com/web-lizard/Forge-Fran-aise.git"

BACKEND_PORT = 8797
FRONTEND_PORT = 5197

GIT_NAME = "web-lizard"
GIT_EMAIL = "web-lizard@users.noreply.github.com"


def clean(content: str) -> str:
    return textwrap.dedent(content).lstrip("\n").rstrip() + "\n"


def w(rel_path: str, content: str = "") -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(clean(content), encoding="utf-8")
    print(f"written: {rel_path}")


def mkdir(rel_path: str) -> None:
    path = ROOT / rel_path
    path.mkdir(parents=True, exist_ok=True)
    print(f"dir: {rel_path}")


def run(cmd: list[str], cwd: Path = ROOT) -> int:
    print("")
    print("RUN:", " ".join(cmd))
    try:
        result = subprocess.run(cmd, cwd=str(cwd), check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"skip, command not found: {' '.join(cmd)}")
        return 127


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Project directory not found: {ROOT}")

    print("Forge Francaise patch 3")
    print("Step 3/6: course content, section page, card renderer, git identity")
    print(f"root: {ROOT}")
    print("")

    for rel in [
        "content/sections/01_pronunciation/lessons",
        "content/sections/04_nouns/lessons",
        "content/sections/05_verbs/lessons",
        "content/sections/06_phrasebook/lessons",
        "frontend/src/components/learning",
        "frontend/src/components/practice",
        "frontend/src/pages",
        "backend/app/api",
        "backend/app/services",
        "scripts",
    ]:
        mkdir(rel)

    w("content/sections/01_pronunciation/section.json", """
    {
      "id": "pronunciation",
      "slug": "pronunciation",
      "order": 1,
      "icon": "sound",
      "title": {
        "ru": "Произношение",
        "fr": "Prononciation"
      },
      "subtitle": {
        "ru": "Звуки, носовые гласные, r и французские странности на слух.",
        "fr": "Les sons, les nasales, le r et les étrangetés françaises."
      },
      "level": "A0",
      "tone": "phonetics",
      "lessons": ["sounds_001", "silent_letters_001"],
      "is_adult": false
    }
    """)

    w("content/sections/01_pronunciation/lessons/sounds_001.json", """
    {
      "id": "sounds_001",
      "section_id": "pronunciation",
      "order": 1,
      "level": "A0",
      "title": {
        "ru": "Первые звуки: bonjour, merci, oui",
        "fr": "Premiers sons : bonjour, merci, oui"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Сначала слушаем",
            "fr": "On écoute d’abord"
          },
          "body": {
            "ru": "Французский нельзя нормально взять только глазами. Слова надо сразу слушать, иначе bonjour останется буквами, а не звуком.",
            "fr": "Le français doit être écouté dès le début. Les mots doivent devenir des sons."
          }
        },
        {
          "type": "word",
          "fr": "oui",
          "transcription": "[уи]",
          "ru": "да",
          "audio_text": "oui",
          "tooltip": {
            "ru": "Очень короткое базовое слово. Звучит примерно как уи.",
            "fr": "Mot très court et très courant."
          }
        },
        {
          "type": "word",
          "fr": "non",
          "transcription": "[нон]",
          "ru": "нет",
          "audio_text": "non",
          "tooltip": {
            "ru": "Базовое нет. Носовой звук здесь пока можно воспринимать примерно как нон.",
            "fr": "Négation simple et très courante."
          }
        },
        {
          "type": "example",
          "fr": "Oui, monsieur.",
          "transcription": "[уи, месьё]",
          "ru": "Да, месье.",
          "audio_text": "Oui, monsieur."
        },
        {
          "type": "exercise",
          "exercise_id": "ex_oui_translation_001"
        }
      ],
      "exercises": [
        {
          "id": "ex_oui_translation_001",
          "type": "choose_option",
          "prompt": {
            "ru": "Что значит oui?",
            "fr": "Que signifie oui ?"
          },
          "options": ["да", "нет", "спасибо", "пожалуйста"],
          "answer": "да",
          "explanation": {
            "ru": "oui значит да.",
            "fr": "oui signifie oui."
          },
          "audio_text": "oui",
          "tags": ["pronunciation", "basic"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("content/sections/01_pronunciation/lessons/silent_letters_001.json", """
    {
      "id": "silent_letters_001",
      "section_id": "pronunciation",
      "order": 2,
      "level": "A0",
      "title": {
        "ru": "Немые буквы: почему не всё читается",
        "fr": "Lettres muettes : pourquoi tout ne se prononce pas"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Французский пишет больше, чем говорит",
            "fr": "Le français écrit plus qu’il ne parle"
          },
          "body": {
            "ru": "Во французском последние буквы часто не произносятся. Это не баг, это отдельная система. Сначала просто привыкаем: beaucoup звучит не как буквальная мясорубка.",
            "fr": "En français, les lettres finales sont souvent muettes."
          }
        },
        {
          "type": "word",
          "fr": "beaucoup",
          "transcription": "[боку]",
          "ru": "много / очень",
          "audio_text": "beaucoup",
          "tooltip": {
            "ru": "Последняя p не произносится. Слово звучит примерно как боку.",
            "fr": "La dernière lettre ne se prononce pas."
          }
        },
        {
          "type": "example",
          "fr": "Merci beaucoup.",
          "transcription": "[мэрси боку]",
          "ru": "Большое спасибо.",
          "audio_text": "Merci beaucoup."
        },
        {
          "type": "exercise",
          "exercise_id": "ex_beaucoup_sound_001"
        }
      ],
      "exercises": [
        {
          "id": "ex_beaucoup_sound_001",
          "type": "choose_option",
          "prompt": {
            "ru": "Как примерно звучит beaucoup?",
            "fr": "Comment se prononce beaucoup ?"
          },
          "options": ["боку", "беаукоуп", "бекоп", "бокоуп"],
          "answer": "боку",
          "explanation": {
            "ru": "beaucoup звучит примерно как боку. Последняя p молчит.",
            "fr": "beaucoup se prononce à peu près comme боку."
          },
          "audio_text": "beaucoup",
          "tags": ["pronunciation", "silent_letters"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("content/sections/02_articles/section.json", """
    {
      "id": "articles",
      "slug": "articles",
      "order": 2,
      "icon": "shield",
      "title": {
        "ru": "Артикли",
        "fr": "Les articles"
      },
      "subtitle": {
        "ru": "Le, la, les, un, une, des без мозгового тумана.",
        "fr": "Le, la, les, un, une, des sans brouillard."
      },
      "level": "A0",
      "tone": "grammar",
      "lessons": ["le_la_001", "un_une_des_001"],
      "is_adult": false
    }
    """)

    w("content/sections/02_articles/lessons/un_une_des_001.json", """
    {
      "id": "un_une_des_001",
      "section_id": "articles",
      "order": 2,
      "level": "A0",
      "title": {
        "ru": "Un, une, des: какой-то, какая-то, какие-то",
        "fr": "Un, une, des : indéfini"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Определённое и неопределённое",
            "fr": "Défini et indéfini"
          },
          "body": {
            "ru": "le/la говорят о чём-то определённом или общем. un/une/des часто работают как какой-то, какая-то, какие-то.",
            "fr": "un, une et des introduisent souvent quelque chose de non précisé."
          }
        },
        {
          "type": "word",
          "fr": "un",
          "transcription": "[эн]",
          "ru": "неопределённый артикль мужского рода",
          "audio_text": "un",
          "tooltip": {
            "ru": "un livre - какая-то книга или одна книга. livre мужского рода.",
            "fr": "Article indéfini masculin singulier."
          }
        },
        {
          "type": "word",
          "fr": "une",
          "transcription": "[юн]",
          "ru": "неопределённый артикль женского рода",
          "audio_text": "une",
          "tooltip": {
            "ru": "une maison - какой-то дом. maison женского рода во французском.",
            "fr": "Article indéfini féminin singulier."
          }
        },
        {
          "type": "word",
          "fr": "des",
          "transcription": "[дэ]",
          "ru": "неопределённый артикль множественного числа",
          "audio_text": "des",
          "tooltip": {
            "ru": "des livres - какие-то книги.",
            "fr": "Article indéfini pluriel."
          }
        },
        {
          "type": "exercise",
          "exercise_id": "ex_une_maison_001"
        }
      ],
      "exercises": [
        {
          "id": "ex_une_maison_001",
          "type": "choose_option",
          "prompt": {
            "ru": "Выбери правильную форму: ___ maison",
            "fr": "Choisis la bonne forme : ___ maison"
          },
          "options": ["un", "une", "des", "le"],
          "answer": "une",
          "explanation": {
            "ru": "maison женского рода, поэтому une maison.",
            "fr": "maison est féminin, donc une maison."
          },
          "audio_text": "une maison",
          "tags": ["article", "indefinite", "gender"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("content/sections/04_nouns/section.json", """
    {
      "id": "nouns",
      "slug": "nouns",
      "order": 4,
      "icon": "book",
      "title": {
        "ru": "Род и число",
        "fr": "Genre et nombre"
      },
      "subtitle": {
        "ru": "Почему maison женского рода, а livre мужского, и как с этим жить.",
        "fr": "Masculin, féminin, singulier et pluriel."
      },
      "level": "A0",
      "tone": "grammar",
      "lessons": ["gender_001", "plural_001"],
      "is_adult": false
    }
    """)

    w("content/sections/04_nouns/lessons/gender_001.json", """
    {
      "id": "gender_001",
      "section_id": "nouns",
      "order": 1,
      "level": "A0",
      "title": {
        "ru": "Род существительных",
        "fr": "Le genre des noms"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Род не обязан совпадать с русским",
            "fr": "Le genre ne suit pas le russe"
          },
          "body": {
            "ru": "Во французском у существительных есть грамматический род. Он не обязан совпадать с русским. Дом по-русски мужской, но maison во французском женского рода.",
            "fr": "En français, les noms ont un genre grammatical : masculin ou féminin."
          }
        },
        {
          "type": "example",
          "fr": "la maison",
          "transcription": "[ля мэзон]",
          "ru": "дом",
          "audio_text": "la maison"
        },
        {
          "type": "example",
          "fr": "le livre",
          "transcription": "[лё ливр]",
          "ru": "книга",
          "audio_text": "le livre"
        },
        {
          "type": "exercise",
          "exercise_id": "ex_gender_livre_001"
        }
      ],
      "exercises": [
        {
          "id": "ex_gender_livre_001",
          "type": "choose_option",
          "prompt": {
            "ru": "Как правильно: ___ livre",
            "fr": "Quelle forme est correcte : ___ livre"
          },
          "options": ["le", "la", "une", "de la"],
          "answer": "le",
          "explanation": {
            "ru": "livre мужского рода, поэтому le livre.",
            "fr": "livre est masculin, donc le livre."
          },
          "audio_text": "le livre",
          "tags": ["noun", "gender", "article"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("content/sections/04_nouns/lessons/plural_001.json", """
    {
      "id": "plural_001",
      "section_id": "nouns",
      "order": 2,
      "level": "A0",
      "title": {
        "ru": "Множественное число",
        "fr": "Le pluriel"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Les - когда предметов несколько",
            "fr": "Les - quand il y en a plusieurs"
          },
          "body": {
            "ru": "Для множественного числа определённый артикль обычно les. И он не различает мужской и женский род.",
            "fr": "Au pluriel, l’article défini est les."
          }
        },
        {
          "type": "example",
          "fr": "les livres",
          "transcription": "[ле ливр]",
          "ru": "книги",
          "audio_text": "les livres"
        },
        {
          "type": "example",
          "fr": "les maisons",
          "transcription": "[ле мэзон]",
          "ru": "дома",
          "audio_text": "les maisons"
        },
        {
          "type": "exercise",
          "exercise_id": "ex_plural_les_001"
        }
      ],
      "exercises": [
        {
          "id": "ex_plural_les_001",
          "type": "choose_option",
          "prompt": {
            "ru": "Выбери артикль для множественного числа: ___ maisons",
            "fr": "Choisis l’article pluriel : ___ maisons"
          },
          "options": ["le", "la", "les", "un"],
          "answer": "les",
          "explanation": {
            "ru": "Во множественном числе используется les: les maisons.",
            "fr": "Au pluriel, on utilise les : les maisons."
          },
          "audio_text": "les maisons",
          "tags": ["plural", "article"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("content/sections/05_verbs/section.json", """
    {
      "id": "verbs",
      "slug": "verbs",
      "order": 5,
      "icon": "sword",
      "title": {
        "ru": "Базовые глаголы",
        "fr": "Verbes de base"
      },
      "subtitle": {
        "ru": "Être, avoir, aller, faire - четыре двигателя фразы.",
        "fr": "Être, avoir, aller, faire - quatre moteurs de phrase."
      },
      "level": "A0",
      "tone": "grammar",
      "lessons": ["etre_avoir_001", "aller_faire_001"],
      "is_adult": false
    }
    """)

    w("content/sections/05_verbs/lessons/etre_avoir_001.json", """
    {
      "id": "etre_avoir_001",
      "section_id": "verbs",
      "order": 1,
      "level": "A0",
      "title": {
        "ru": "Être и avoir: быть и иметь",
        "fr": "Être et avoir"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Два главных глагола",
            "fr": "Deux verbes essentiels"
          },
          "body": {
            "ru": "être - быть. avoir - иметь. На них держится огромная часть французской грамматики.",
            "fr": "être signifie être. avoir signifie avoir."
          }
        },
        {
          "type": "word",
          "fr": "je suis",
          "transcription": "[жё сюи]",
          "ru": "я есть / я являюсь",
          "audio_text": "je suis",
          "tooltip": {
            "ru": "Форма глагола être для je.",
            "fr": "Forme de être avec je."
          }
        },
        {
          "type": "word",
          "fr": "j’ai",
          "transcription": "[жэ]",
          "ru": "у меня есть / я имею",
          "audio_text": "j’ai",
          "tooltip": {
            "ru": "Форма глагола avoir для je. Je + ai сливаются в j’ai.",
            "fr": "Forme de avoir avec je."
          }
        },
        {
          "type": "example",
          "fr": "Je suis prêt.",
          "transcription": "[жё сюи прэ]",
          "ru": "Я готов.",
          "audio_text": "Je suis prêt."
        },
        {
          "type": "exercise",
          "exercise_id": "ex_je_suis_001"
        }
      ],
      "exercises": [
        {
          "id": "ex_je_suis_001",
          "type": "choose_option",
          "prompt": {
            "ru": "Как сказать я есть / я являюсь?",
            "fr": "Comment dire je suis ?"
          },
          "options": ["je suis", "j’ai", "je vais", "merci"],
          "answer": "je suis",
          "explanation": {
            "ru": "je suis - это я есть / я являюсь.",
            "fr": "je suis est la forme de être avec je."
          },
          "audio_text": "je suis",
          "tags": ["verb", "etre"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("content/sections/05_verbs/lessons/aller_faire_001.json", """
    {
      "id": "aller_faire_001",
      "section_id": "verbs",
      "order": 2,
      "level": "A0",
      "title": {
        "ru": "Aller и faire: идти и делать",
        "fr": "Aller et faire"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Движение и действие",
            "fr": "Mouvement et action"
          },
          "body": {
            "ru": "aller - идти или ехать. faire - делать. Это базовые рабочие глаголы на каждый день.",
            "fr": "aller exprime le mouvement. faire exprime l’action."
          }
        },
        {
          "type": "word",
          "fr": "je vais",
          "transcription": "[жё вэ]",
          "ru": "я иду / я еду",
          "audio_text": "je vais",
          "tooltip": {
            "ru": "Форма глагола aller для je.",
            "fr": "Forme de aller avec je."
          }
        },
        {
          "type": "word",
          "fr": "je fais",
          "transcription": "[жё фэ]",
          "ru": "я делаю",
          "audio_text": "je fais",
          "tooltip": {
            "ru": "Форма глагола faire для je.",
            "fr": "Forme de faire avec je."
          }
        },
        {
          "type": "example",
          "fr": "Je fais le test.",
          "transcription": "[жё фэ лё тэст]",
          "ru": "Я делаю тест.",
          "audio_text": "Je fais le test."
        },
        {
          "type": "exercise",
          "exercise_id": "ex_je_fais_001"
        }
      ],
      "exercises": [
        {
          "id": "ex_je_fais_001",
          "type": "choose_option",
          "prompt": {
            "ru": "Как сказать я делаю?",
            "fr": "Comment dire je fais ?"
          },
          "options": ["je vais", "je fais", "je suis", "j’ai"],
          "answer": "je fais",
          "explanation": {
            "ru": "je fais значит я делаю.",
            "fr": "je fais signifie я делаю."
          },
          "audio_text": "je fais",
          "tags": ["verb", "faire"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("content/sections/06_phrasebook/section.json", """
    {
      "id": "phrasebook",
      "slug": "phrasebook",
      "order": 6,
      "icon": "banner",
      "title": {
        "ru": "Фразовый арсенал",
        "fr": "Arsenal de phrases"
      },
      "subtitle": {
        "ru": "Нормальные фразы плюс имперская ебанистика для запоминания.",
        "fr": "Phrases utiles avec une touche impériale."
      },
      "level": "A0",
      "tone": "phrasebook",
      "lessons": ["basic_phrases_001", "imperial_phrases_001"],
      "is_adult": false
    }
    """)

    w("content/sections/06_phrasebook/lessons/basic_phrases_001.json", """
    {
      "id": "basic_phrases_001",
      "section_id": "phrasebook",
      "order": 1,
      "level": "A0",
      "title": {
        "ru": "Первые полезные фразы",
        "fr": "Premières phrases utiles"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Фразы нужны сразу",
            "fr": "Les phrases sont nécessaires tout de suite"
          },
          "body": {
            "ru": "Отдельные слова важны, но мозг лучше цепляется за короткие живые фразы.",
            "fr": "Le cerveau retient mieux les phrases courtes."
          }
        },
        {
          "type": "example",
          "fr": "Je ne comprends pas.",
          "transcription": "[жё нё компрэн па]",
          "ru": "Я не понимаю.",
          "audio_text": "Je ne comprends pas."
        },
        {
          "type": "example",
          "fr": "Parlez lentement, s’il vous plaît.",
          "transcription": "[парле лантман, силь ву пле]",
          "ru": "Говорите медленно, пожалуйста.",
          "audio_text": "Parlez lentement, s’il vous plaît."
        },
        {
          "type": "exercise",
          "exercise_id": "ex_je_ne_comprends_pas_001"
        }
      ],
      "exercises": [
        {
          "id": "ex_je_ne_comprends_pas_001",
          "type": "choose_option",
          "prompt": {
            "ru": "Что значит Je ne comprends pas?",
            "fr": "Que signifie Je ne comprends pas ?"
          },
          "options": ["Я не понимаю", "Я готов", "Я хочу воды", "Здравствуйте"],
          "answer": "Я не понимаю",
          "explanation": {
            "ru": "Je ne comprends pas - я не понимаю.",
            "fr": "Je ne comprends pas signifie я не понимаю."
          },
          "audio_text": "Je ne comprends pas.",
          "tags": ["phrase", "basic"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("content/sections/06_phrasebook/lessons/imperial_phrases_001.json", """
    {
      "id": "imperial_phrases_001",
      "section_id": "phrasebook",
      "order": 2,
      "level": "A0",
      "title": {
        "ru": "Имперские фразы",
        "fr": "Phrases impériales"
      },
      "cards": [
        {
          "type": "theory",
          "title": {
            "ru": "Пафос помогает памяти",
            "fr": "Le panache aide la mémoire"
          },
          "body": {
            "ru": "Чем страннее и ярче фраза, тем легче мозгу её удержать. Поэтому да, тут будет империя.",
            "fr": "Une phrase vive et étrange se retient plus facilement."
          }
        },
        {
          "type": "example",
          "fr": "Je suis souverain.",
          "transcription": "[жё сюи сувэрэн]",
          "ru": "Я суверенен.",
          "audio_text": "Je suis souverain."
        },
        {
          "type": "example",
          "fr": "Nous sommes des lézards.",
          "transcription": "[ну сом дэ лезар]",
          "ru": "Мы ящеры.",
          "audio_text": "Nous sommes des lézards."
        },
        {
          "type": "example",
          "fr": "Vive l’Empire.",
          "transcription": "[вив ланпир]",
          "ru": "Да здравствует Империя.",
          "audio_text": "Vive l’Empire."
        },
        {
          "type": "exercise",
          "exercise_id": "ex_je_suis_souverain_001"
        }
      ],
      "exercises": [
        {
          "id": "ex_je_suis_souverain_001",
          "type": "choose_option",
          "prompt": {
            "ru": "Что значит Je suis souverain?",
            "fr": "Que signifie Je suis souverain ?"
          },
          "options": ["Я суверенен", "Я устал", "Я иду", "Я не понимаю"],
          "answer": "Я суверенен",
          "explanation": {
            "ru": "Je suis - я есть / я являюсь. souverain - суверенный.",
            "fr": "Je suis souverain signifie я суверенен."
          },
          "audio_text": "Je suis souverain.",
          "tags": ["phrase", "imperial", "etre"],
          "difficulty": 1
        }
      ]
    }
    """)

    w("content/vulgar/packs/office_rage.json", """
    {
      "id": "office_rage",
      "title": {
        "ru": "Офисная злость",
        "fr": "Colère de bureau"
      },
      "items": [
        {
          "id": "c_est_quoi_ce_bordel",
          "fr": "C’est quoi ce bordel ?",
          "transcription": "[сэ куа сё бордэль]",
          "ru": "Что это за херня?",
          "literal_ru": "Что это за бардак?",
          "register": "vulgar",
          "rudeness_level": 4,
          "danger_level": 3,
          "context": {
            "ru": "Грубое возмущение. Часто слышно в разговорной речи, но на официальной встрече лучше не надо.",
            "fr": "Expression vulgaire de surprise ou de colère."
          },
          "softer_versions": [
            {
              "fr": "Qu’est-ce que c’est ?",
              "transcription": "[кэскё сэ]",
              "ru": "Что это такое?"
            }
          ],
          "audio_text": "C’est quoi ce bordel ?",
          "tags": ["vulgar", "office", "anger"]
        },
        {
          "id": "j_en_ai_ras_le_bol",
          "fr": "J’en ai ras le bol.",
          "transcription": "[жанэ ра лё боль]",
          "ru": "Меня это достало по горло.",
          "literal_ru": "У меня этого полная миска.",
          "register": "familiar",
          "rudeness_level": 3,
          "danger_level": 2,
          "context": {
            "ru": "Разговорное выражение сильной усталости или раздражения. Менее грубо, чем прямой мат.",
            "fr": "Expression familière de lassitude."
          },
          "softer_versions": [
            {
              "fr": "Je suis fatigué de ça.",
              "transcription": "[жё сюи фатигэ дэ са]",
              "ru": "Я устал от этого."
            }
          ],
          "audio_text": "J’en ai ras le bol.",
          "tags": ["familiar", "office", "anger"]
        }
      ]
    }
    """)

    w("content/vulgar/index.json", """
    {
      "title": {
        "ru": "Французский мат",
        "fr": "Les gros mots français"
      },
      "is_adult": true,
      "categories": [
        {
          "id": "anger_basic",
          "title": {
            "ru": "Базовая злость",
            "fr": "Colère de base"
          }
        },
        {
          "id": "go_away",
          "title": {
            "ru": "Как послать человека",
            "fr": "Envoyer quelqu’un balader"
          }
        },
        {
          "id": "office_rage",
          "title": {
            "ru": "Офисная злость",
            "fr": "Colère de bureau"
          }
        }
      ]
    }
    """)

    w("content/codex/pronunciation.json", """
    {
      "id": "pronunciation",
      "title": {
        "ru": "Произношение",
        "fr": "Prononciation"
      },
      "summary": {
        "ru": "Французский нужно слушать с первого дня. Написание и звучание часто расходятся.",
        "fr": "Le français doit être écouté dès le début."
      },
      "items": [
        {
          "fr": "beaucoup",
          "transcription": "[боку]",
          "ru": "много / очень, последняя p не читается"
        },
        {
          "fr": "oui",
          "transcription": "[уи]",
          "ru": "да"
        },
        {
          "fr": "non",
          "transcription": "[нон]",
          "ru": "нет"
        }
      ]
    }
    """)

    w("content/codex/verbs.json", """
    {
      "id": "verbs",
      "title": {
        "ru": "Базовые глаголы",
        "fr": "Verbes de base"
      },
      "summary": {
        "ru": "Être, avoir, aller и faire - главные рабочие глаголы для старта.",
        "fr": "Être, avoir, aller et faire sont essentiels."
      },
      "items": [
        {
          "fr": "je suis",
          "transcription": "[жё сюи]",
          "ru": "я есть / я являюсь"
        },
        {
          "fr": "j’ai",
          "transcription": "[жэ]",
          "ru": "у меня есть / я имею"
        },
        {
          "fr": "je vais",
          "transcription": "[жё вэ]",
          "ru": "я иду / я еду"
        },
        {
          "fr": "je fais",
          "transcription": "[жё фэ]",
          "ru": "я делаю"
        }
      ]
    }
    """)

    w("backend/app/services/course_service.py", """
    from typing import Any

    from app.services.content_service import get_content_service


    class CourseService:
        def course_map(self) -> dict[str, Any]:
            content = get_content_service()
            sections = content.list_sections()
            result_sections = []

            for section in sections:
                lessons = []
                for lesson_id in section.get("lessons", []):
                    lesson = content.get_lesson(lesson_id)
                    lessons.append({
                        "id": lesson["id"],
                        "section_id": lesson["section_id"],
                        "order": lesson.get("order", 999),
                        "level": lesson.get("level", "A0"),
                        "title": lesson["title"],
                        "card_count": len(lesson.get("cards", [])),
                        "exercise_count": len(lesson.get("exercises", [])),
                    })

                item = dict(section)
                item["lesson_items"] = sorted(lessons, key=lambda lesson: lesson.get("order", 999))
                result_sections.append(item)

            return {
                "sections": result_sections,
                "total_sections": len(result_sections),
                "total_lessons": sum(len(section["lesson_items"]) for section in result_sections),
            }

        def section_with_lessons(self, section_id: str) -> dict[str, Any]:
            content = get_content_service()
            section = dict(content.get_section(section_id))
            lessons = []

            for lesson_id in section.get("lessons", []):
                lesson = content.get_lesson(lesson_id)
                lessons.append({
                    "id": lesson["id"],
                    "section_id": lesson["section_id"],
                    "order": lesson.get("order", 999),
                    "level": lesson.get("level", "A0"),
                    "title": lesson["title"],
                    "card_count": len(lesson.get("cards", [])),
                    "exercise_count": len(lesson.get("exercises", [])),
                })

            section["lesson_items"] = sorted(lessons, key=lambda lesson: lesson.get("order", 999))
            return section


    def get_course_service() -> CourseService:
        return CourseService()
    """)

    w("backend/app/api/course.py", """
    from fastapi import APIRouter, HTTPException

    from app.services.course_service import get_course_service

    router = APIRouter(tags=["course"])


    @router.get("/course")
    def course_map():
        return get_course_service().course_map()


    @router.get("/course/sections/{section_id}")
    def section_with_lessons(section_id: str):
        try:
            return get_course_service().section_with_lessons(section_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error))
    """)

    w("backend/app/main.py", """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from app.api import audio, bootstrap, codex, course, health, lessons, practice, profiles, progress, sections, settings, vulgar

    app = FastAPI(
        title="Forge Française API",
        description="Imperial French learning engine",
        version="0.3.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5197",
            "http://localhost:5197",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(settings.router, prefix="/api")
    app.include_router(bootstrap.router, prefix="/api")
    app.include_router(course.router, prefix="/api")
    app.include_router(sections.router, prefix="/api")
    app.include_router(lessons.router, prefix="/api")
    app.include_router(practice.router, prefix="/api")
    app.include_router(progress.router, prefix="/api")
    app.include_router(profiles.router, prefix="/api")
    app.include_router(audio.router, prefix="/api")
    app.include_router(codex.router, prefix="/api")
    app.include_router(vulgar.router, prefix="/api")
    """)

    w("frontend/src/router/index.ts", """
    import { createRouter, createWebHistory } from 'vue-router'

    import ThronePage from '../pages/ThronePage.vue'
    import CampaignPage from '../pages/CampaignPage.vue'
    import SectionPage from '../pages/SectionPage.vue'
    import LessonPage from '../pages/LessonPage.vue'
    import PracticePage from '../pages/PracticePage.vue'
    import CodexPage from '../pages/CodexPage.vue'
    import VulgarLibraryPage from '../pages/VulgarLibraryPage.vue'
    import ProfilePage from '../pages/ProfilePage.vue'

    export const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', name: 'throne', component: ThronePage },
        { path: '/campaign', name: 'campaign', component: CampaignPage },
        { path: '/section/:sectionId', name: 'section', component: SectionPage },
        { path: '/lesson/:lessonId', name: 'lesson', component: LessonPage },
        { path: '/practice', name: 'practice', component: PracticePage },
        { path: '/codex', name: 'codex', component: CodexPage },
        { path: '/vulgar', name: 'vulgar', component: VulgarLibraryPage },
        { path: '/profile', name: 'profile', component: ProfilePage },
      ],
    })
    """)

    w("frontend/src/components/learning/LessonTile.vue", """
    <script setup lang="ts">
    import { t } from '../../lib/i18n'
    import { useSettingsStore } from '../../stores/settingsStore'

    defineProps<{
      lesson: any
    }>()

    const settings = useSettingsStore()
    </script>

    <template>
      <RouterLink class="lesson-tile lesson-tile-vertical" :to="'/lesson/' + lesson.id">
        <div class="lesson-meta">
          <span>{{ lesson.level }}</span>
          <span>{{ lesson.card_count }} cards</span>
          <span>{{ lesson.exercise_count }} drill</span>
        </div>
        <strong>{{ t(lesson.title, settings.uiLanguage) }}</strong>
      </RouterLink>
    </template>
    """)

    w("frontend/src/pages/SectionPage.vue", """
    <script setup lang="ts">
    import { onMounted, ref, watch } from 'vue'
    import { useRoute } from 'vue-router'
    import { apiGet } from '../lib/api'
    import { t } from '../lib/i18n'
    import LessonTile from '../components/learning/LessonTile.vue'
    import { useSettingsStore } from '../stores/settingsStore'

    const route = useRoute()
    const settings = useSettingsStore()
    const section = ref<any | null>(null)
    const loading = ref(false)

    async function loadSection() {
      loading.value = true
      section.value = await apiGet<any>('/course/sections/' + route.params.sectionId)
      loading.value = false
    }

    onMounted(loadSection)
    watch(() => route.params.sectionId, loadSection)
    </script>

    <template>
      <section class="page">
        <div v-if="loading" class="soft-card">Загрузка...</div>

        <template v-if="section">
          <div class="section-title">
            <div class="eyebrow">{{ section.level }} / {{ section.tone }}</div>
            <h1>{{ t(section.title, settings.uiLanguage) }}</h1>
            <p>{{ t(section.subtitle, settings.uiLanguage) }}</p>
          </div>

          <div class="card-list">
            <LessonTile
              v-for="lesson in section.lesson_items"
              :key="lesson.id"
              :lesson="lesson"
            />
          </div>
        </template>
      </section>
    </template>
    """)

    w("frontend/src/pages/CampaignPage.vue", """
    <script setup lang="ts">
    import { onMounted, ref } from 'vue'
    import { apiGet } from '../lib/api'
    import { t } from '../lib/i18n'
    import { useSettingsStore } from '../stores/settingsStore'

    const settings = useSettingsStore()
    const course = ref<any | null>(null)

    onMounted(async () => {
      course.value = await apiGet<any>('/course')
    })
    </script>

    <template>
      <section class="page">
        <div class="section-title">
          <div class="eyebrow">Campagne</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Учебные секции' : 'Sections' }}</h1>
          <p v-if="course">
            {{ course.total_sections }} sections / {{ course.total_lessons }} lessons
          </p>
        </div>

        <div class="card-list">
          <RouterLink
            v-for="section in course?.sections ?? []"
            :key="section.id"
            class="lesson-tile"
            :to="section.id === 'vulgar_french' ? '/vulgar' : '/section/' + section.id"
          >
            <div class="tile-icon">{{ section.icon }}</div>
            <div>
              <strong>{{ t(section.title, settings.uiLanguage) }}</strong>
              <span>{{ t(section.subtitle, settings.uiLanguage) }}</span>
              <small>{{ section.lesson_items.length }} lessons</small>
            </div>
          </RouterLink>
        </div>
      </section>
    </template>
    """)

    w("frontend/src/components/learning/CardRenderer.vue", """
    <script setup lang="ts">
    import { t, ui } from '../../lib/i18n'
    import { useSettingsStore } from '../../stores/settingsStore'
    import AudioButton from './AudioButton.vue'
    import ExerciseRenderer from '../practice/ExerciseRenderer.vue'

    const props = defineProps<{
      lesson: any
      card: any
    }>()

    const settings = useSettingsStore()

    function exerciseById(exerciseId: string) {
      return props.lesson?.exercises?.find((item: any) => item.id === exerciseId)
    }

    function explain(card: any) {
      const title = settings.uiLanguage === 'ru' ? 'Пояснение' : 'Explication'
      const body = card.tooltip
        ? t(card.tooltip, settings.uiLanguage)
        : settings.uiLanguage === 'ru'
          ? 'Подробный разбор будет добавлен в Кодекс.'
          : 'Une explication détaillée sera ajoutée au Codex.'

      settings.openSheet(title, body)
    }
    </script>

    <template>
      <article class="study-card">
        <template v-if="card.type === 'theory'">
          <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Теория' : 'Théorie' }}</div>
          <h2>{{ t(card.title, settings.uiLanguage) }}</h2>
          <p>{{ t(card.body, settings.uiLanguage) }}</p>
          <button
            class="ghost-button wide"
            type="button"
            @click="settings.openSheet(t(card.title, settings.uiLanguage), t(card.body, settings.uiLanguage))"
          >
            {{ ui('why', settings.uiLanguage) }}
          </button>
        </template>

        <template v-else-if="card.type === 'word'">
          <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Слово' : 'Mot' }}</div>
          <h2>{{ card.fr }}</h2>
          <p class="transcription">{{ card.transcription }}</p>
          <p>{{ card.ru }}</p>
          <div class="button-row">
            <AudioButton :text="card.audio_text" :label="ui('listen', settings.uiLanguage)" />
            <button class="ghost-button" type="button" @click="explain(card)">
              ?
            </button>
          </div>
        </template>

        <template v-else-if="card.type === 'example'">
          <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Пример' : 'Exemple' }}</div>
          <h2>{{ card.fr }}</h2>
          <p class="transcription">{{ card.transcription }}</p>
          <p>{{ card.ru }}</p>
          <AudioButton :text="card.audio_text" :label="ui('listen', settings.uiLanguage)" />
        </template>

        <template v-else-if="card.type === 'exercise'">
          <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Упражнение' : 'Exercice' }}</div>
          <ExerciseRenderer
            v-if="exerciseById(card.exercise_id)"
            :lesson-id="lesson.id"
            :exercise="exerciseById(card.exercise_id)"
          />
        </template>
      </article>
    </template>
    """)

    w("frontend/src/pages/LessonPage.vue", """
    <script setup lang="ts">
    import { computed, onMounted, ref, watch } from 'vue'
    import { useRoute } from 'vue-router'
    import CardRenderer from '../components/learning/CardRenderer.vue'
    import { apiGet } from '../lib/api'
    import { t } from '../lib/i18n'
    import { useSettingsStore } from '../stores/settingsStore'

    const route = useRoute()
    const settings = useSettingsStore()
    const lesson = ref<any | null>(null)
    const loading = ref(false)
    const cardIndex = ref(0)

    const currentCard = computed(() => lesson.value?.cards?.[cardIndex.value] ?? null)
    const totalCards = computed(() => lesson.value?.cards?.length ?? 0)

    async function loadLesson() {
      loading.value = true
      cardIndex.value = 0
      lesson.value = await apiGet<any>('/lessons/' + route.params.lessonId)
      loading.value = false
    }

    function nextCard() {
      if (cardIndex.value < totalCards.value - 1) {
        cardIndex.value += 1
      }
    }

    function prevCard() {
      if (cardIndex.value > 0) {
        cardIndex.value -= 1
      }
    }

    onMounted(loadLesson)
    watch(() => route.params.lessonId, loadLesson)
    </script>

    <template>
      <section class="page lesson-page">
        <div v-if="loading" class="soft-card">Загрузка...</div>

        <template v-if="lesson && currentCard">
          <div class="section-title compact-title">
            <div class="eyebrow">{{ lesson.level }} / {{ cardIndex + 1 }} из {{ totalCards }}</div>
            <h1>{{ t(lesson.title, settings.uiLanguage) }}</h1>
          </div>

          <div class="lesson-progress">
            <div :style="{ width: ((cardIndex + 1) / totalCards * 100) + '%' }"></div>
          </div>

          <CardRenderer :lesson="lesson" :card="currentCard" />

          <div class="lesson-nav-row">
            <button class="ghost-button" type="button" :disabled="cardIndex === 0" @click="prevCard">
              ←
            </button>
            <RouterLink class="ghost-button" to="/campaign">
              {{ settings.uiLanguage === 'ru' ? 'Карта' : 'Carte' }}
            </RouterLink>
            <button class="primary-button" type="button" :disabled="cardIndex >= totalCards - 1" @click="nextCard">
              {{ settings.uiLanguage === 'ru' ? 'Дальше' : 'Suivant' }}
            </button>
          </div>
        </template>
      </section>
    </template>
    """)

    w("frontend/src/styles/imperial.css", """
    .imperial-shell {
      position: relative;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: calc(var(--bottom-nav-height) + 18px);
    }

    .shell-main {
      width: min(100%, 980px);
      margin: 0 auto;
      padding: 14px;
    }

    .top-bar {
      position: sticky;
      top: 0;
      z-index: 20;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px;
      background: rgba(11, 13, 12, 0.82);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(176, 138, 69, 0.25);
    }

    .top-title,
    h1,
    h2 {
      letter-spacing: 0.02em;
    }

    .top-title {
      font-weight: 800;
    }

    .eyebrow {
      color: var(--antique-gold);
      font-size: 0.76rem;
      font-weight: 800;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .page {
      display: grid;
      gap: 14px;
    }

    .hero-card,
    .study-card,
    .soft-card,
    .quick-card,
    .lesson-tile {
      border: 1px solid rgba(232, 226, 216, 0.12);
      background:
        linear-gradient(135deg, rgba(37, 91, 50, 0.28), transparent 38%),
        var(--panel-black);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-soft);
    }

    .hero-card {
      min-height: calc(100vh - 190px);
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 16px;
      padding: 26px;
    }

    .hero-card h1,
    .section-title h1 {
      margin: 0;
      font-size: clamp(2rem, 12vw, 4.6rem);
      line-height: 0.95;
    }

    .compact-title h1 {
      font-size: clamp(1.5rem, 8vw, 2.6rem);
    }

    .hero-card p,
    .section-title p,
    .study-card p {
      color: var(--text-muted);
      line-height: 1.55;
    }

    .crest-orb {
      width: 72px;
      height: 72px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(176, 138, 69, 0.55);
      border-radius: 50%;
      background: radial-gradient(circle, rgba(176, 138, 69, 0.35), rgba(37, 91, 50, 0.25));
      font-size: 2rem;
    }

    .profile-strip {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 12px 14px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.06);
    }

    .hero-actions,
    .quick-grid,
    .option-grid,
    .button-row {
      display: grid;
      gap: 10px;
    }

    .button-row {
      grid-template-columns: 1fr auto;
    }

    .primary-button,
    .audio-button,
    .ghost-button,
    .option-button {
      border: 0;
      border-radius: 999px;
      cursor: pointer;
      font-weight: 800;
    }

    .primary-button,
    .audio-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      min-height: 48px;
      padding: 0 18px;
    }

    .primary-button {
      color: #071009;
      background: linear-gradient(135deg, var(--bone-white), var(--antique-gold));
    }

    .audio-button {
      color: var(--bone-white);
      background: rgba(47, 122, 69, 0.45);
      border: 1px solid rgba(232, 226, 216, 0.14);
    }

    .ghost-button {
      min-height: 40px;
      padding: 0 14px;
      color: var(--bone-white);
      background: rgba(255, 255, 255, 0.08);
    }

    .ghost-button.wide {
      width: 100%;
    }

    .quick-grid {
      grid-template-columns: 1fr;
    }

    .quick-card,
    .lesson-tile,
    .study-card,
    .soft-card {
      padding: 18px;
    }

    .quick-card,
    .lesson-tile {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .lesson-tile-vertical {
      align-items: flex-start;
      flex-direction: column;
    }

    .lesson-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--antique-gold);
      font-size: 0.75rem;
      font-weight: 800;
      text-transform: uppercase;
    }

    .quick-card span,
    .lesson-tile span,
    .lesson-tile small {
      display: block;
      margin-top: 4px;
      color: var(--text-muted);
      font-size: 0.92rem;
    }

    .tile-icon {
      width: 44px;
      height: 44px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border-radius: 16px;
      background: rgba(176, 138, 69, 0.16);
    }

    .card-list {
      display: grid;
      gap: 12px;
    }

    .study-card {
      display: grid;
      gap: 10px;
      min-height: min(420px, calc(100vh - 260px));
      align-content: center;
    }

    .study-card h2 {
      margin: 0;
      font-size: clamp(1.4rem, 9vw, 2.8rem);
    }

    .transcription {
      color: var(--antique-gold) !important;
      font-weight: 700;
    }

    .mini-details {
      padding: 12px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.05);
    }

    .option-grid {
      grid-template-columns: 1fr;
    }

    .option-button {
      min-height: 52px;
      color: var(--bone-white);
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(232, 226, 216, 0.12);
    }

    .option-button.selected {
      outline: 2px solid var(--antique-gold);
    }

    .result-box {
      padding: 14px;
      border-radius: 16px;
    }

    .result-box.good {
      background: rgba(47, 122, 69, 0.24);
    }

    .result-box.bad {
      background: rgba(138, 45, 45, 0.24);
    }

    .codex-row {
      display: grid;
      gap: 4px;
      padding: 10px 0;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }

    .danger-card {
      border-color: rgba(138, 45, 45, 0.45);
    }

    .rudeness {
      width: fit-content;
      padding: 6px 10px;
      border-radius: 999px;
      color: var(--bone-white);
      background: rgba(138, 45, 45, 0.45);
      font-size: 0.8rem;
      font-weight: 900;
    }

    .voice-selector {
      display: grid;
      gap: 8px;
    }

    .voice-selector select {
      width: 100%;
      min-height: 48px;
      padding: 0 14px;
      border-radius: 16px;
      border: 1px solid rgba(232, 226, 216, 0.16);
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.08);
    }

    .sheet-backdrop {
      position: fixed;
      inset: 0;
      z-index: 80;
      display: flex;
      align-items: flex-end;
      background: rgba(0, 0, 0, 0.58);
    }

    .bottom-sheet {
      width: 100%;
      max-height: 76vh;
      overflow: auto;
      padding: 14px 18px 24px;
      border-radius: 28px 28px 0 0;
      border: 1px solid rgba(232, 226, 216, 0.12);
      background: rgba(11, 13, 12, 0.98);
      box-shadow: var(--shadow-soft);
    }

    .sheet-handle {
      width: 54px;
      height: 5px;
      margin: 0 auto 14px;
      border-radius: 999px;
      background: rgba(232, 226, 216, 0.26);
    }

    .sheet-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .sheet-head h2 {
      margin: 0;
    }

    .lesson-progress {
      height: 8px;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
    }

    .lesson-progress div {
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--sovereign-green), var(--antique-gold));
      transition: width 0.2s ease;
    }

    .lesson-nav-row {
      display: grid;
      grid-template-columns: auto 1fr 1fr;
      gap: 10px;
    }

    .lesson-nav-row .ghost-button,
    .lesson-nav-row .primary-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 48px;
    }
    """)

    w("frontend/src/pages/VulgarLibraryPage.vue", """
    <script setup lang="ts">
    import { computed, onMounted, ref } from 'vue'
    import AudioButton from '../components/learning/AudioButton.vue'
    import { apiGet } from '../lib/api'
    import { useSettingsStore } from '../stores/settingsStore'

    const settings = useSettingsStore()
    const items = ref<any[]>([])
    const activeTag = ref('all')

    const filteredItems = computed(() => {
      if (activeTag.value === 'all') return items.value
      return items.value.filter((item) => item.tags?.includes(activeTag.value) || item.pack_id === activeTag.value)
    })

    onMounted(async () => {
      items.value = await apiGet<any[]>('/vulgar/items')
    })
    </script>

    <template>
      <section class="page">
        <div class="section-title">
          <div class="eyebrow">Adult Codex</div>
          <h1>{{ settings.uiLanguage === 'ru' ? 'Французский мат' : 'Gros mots français' }}</h1>
          <p>
            {{
              settings.uiLanguage === 'ru'
                ? 'Грубые фразы с уровнем опасности, переводом и озвучкой.'
                : 'Phrases vulgaires avec niveau de danger et audio.'
            }}
          </p>
        </div>

        <div class="chip-row">
          <button class="ghost-button" type="button" @click="activeTag = 'all'">all</button>
          <button class="ghost-button" type="button" @click="activeTag = 'anger_basic'">anger</button>
          <button class="ghost-button" type="button" @click="activeTag = 'go_away'">go away</button>
          <button class="ghost-button" type="button" @click="activeTag = 'office_rage'">office</button>
        </div>

        <article v-for="item in filteredItems" :key="item.id" class="study-card danger-card">
          <div class="rudeness">Грубость {{ item.rudeness_level }}/5</div>
          <h2>{{ item.fr }}</h2>
          <p class="transcription">{{ item.transcription }}</p>
          <p>{{ item.ru }}</p>
          <AudioButton :text="item.audio_text" label="Слушать" />

          <details class="mini-details">
            <summary>Контекст и мягкий вариант</summary>
            <p>{{ item.context.ru }}</p>
            <p v-if="item.softer_versions?.[0]">
              Мягче: <strong>{{ item.softer_versions[0].fr }}</strong>
              {{ item.softer_versions[0].ru }}
            </p>
          </details>
        </article>
      </section>
    </template>
    """)

    w("frontend/src/styles/mobile.css", """
    .bottom-nav {
      position: fixed;
      left: 10px;
      right: 10px;
      bottom: 10px;
      z-index: 30;
      height: var(--bottom-nav-height);
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 6px;
      padding: 8px;
      border: 1px solid rgba(232, 226, 216, 0.12);
      border-radius: 24px;
      background: rgba(11, 13, 12, 0.9);
      backdrop-filter: blur(16px);
      box-shadow: var(--shadow-soft);
    }

    .bottom-nav a {
      display: grid;
      place-items: center;
      border-radius: 18px;
      color: var(--text-muted);
      font-size: 0.76rem;
      font-weight: 800;
    }

    .bottom-nav a.router-link-active {
      color: #071009;
      background: var(--bone-white);
    }

    .chip-row {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 2px;
    }

    .chip-row .ghost-button {
      flex: 0 0 auto;
    }

    @media (min-width: 760px) {
      .shell-main {
        padding: 24px;
      }

      .quick-grid,
      .option-grid {
        grid-template-columns: repeat(3, 1fr);
      }

      .hero-card {
        min-height: 520px;
      }

      .bottom-nav {
        left: 50%;
        right: auto;
        width: min(620px, calc(100vw - 20px));
        transform: translateX(-50%);
      }

      .card-list {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }
    """)

    w("project.config.json", json.dumps({
        "name": "Forge Francaise",
        "public_title_ru": "Имперский мозговыбиватель французского языка",
        "backend_port": BACKEND_PORT,
        "frontend_port": FRONTEND_PORT,
        "api_base": f"http://127.0.0.1:{BACKEND_PORT}/api",
        "frontend_url": f"http://127.0.0.1:{FRONTEND_PORT}",
        "version": "0.3.0",
        "patch": "patch 3: course content and lesson navigation"
    }, ensure_ascii=False, indent=2))

    w("README.md", f"""
    # Forge Française

    Имперский мозговыбиватель французского языка.

    Mobile-first учебный движок французского языка на Vue 3, FastAPI и JSON-контенте.

    ## Ports

    Backend:
    http://127.0.0.1:{BACKEND_PORT}/api/health

    Frontend:
    http://127.0.0.1:{FRONTEND_PORT}

    ## Быстрый запуск

    scripts\\Forge Francaise Launcher.cmd

    ## Что уже заложено

    - Vue 3 + TypeScript + Vite
    - FastAPI backend
    - JSON content engine
    - profiles / progress / ranks
    - TTS provider architecture
    - audio cache
    - vulgar French library
    - mobile-first UI
    - bottom navigation
    - bottom sheet
    - RU / FR UI switch
    - voice selector
    - storage adapter
    - scalable ExerciseRenderer
    - course API
    - section pages
    - lesson card mode
    - expanded A0 content

    ## Patch 3

    Patch 3 adds:

    - pronunciation section
    - nouns section
    - verbs section
    - phrasebook section
    - more article lessons
    - more vulgar library items
    - course API
    - section page
    - lesson tile component
    - card renderer component
    - mobile one-card lesson flow
    - git local identity fix
    """)

    w("scripts/git_push_patch3.cmd", f"""
    @echo off
    cd /d "%~dp0.."
    git config user.name "{GIT_NAME}"
    git config user.email "{GIT_EMAIL}"
    git init
    git branch -M main
    git remote set-url origin {REMOTE_URL}
    git status --short
    git add .
    git commit -m "patch 3: course content and lesson navigation"
    git push -u origin main
    """)

    print("")
    print("Running content validation...")
    run(["py", "scripts\\validate_content.py"], cwd=ROOT / "backend")

    print("")
    print("Git identity fix...")
    run(["git", "config", "user.name", GIT_NAME])
    run(["git", "config", "user.email", GIT_EMAIL])

    print("")
    print("Git setup...")
    run(["git", "init"])
    run(["git", "branch", "-M", "main"])

    remote_result = subprocess.run(
        ["git", "remote"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    remotes = remote_result.stdout.splitlines() if remote_result.returncode == 0 else []

    if "origin" in remotes:
        run(["git", "remote", "set-url", "origin", REMOTE_URL])
    else:
        run(["git", "remote", "add", "origin", REMOTE_URL])

    print("")
    print("Git commit...")
    run(["git", "add", "."])
    commit_code = run(["git", "commit", "-m", "patch 3: course content and lesson navigation"])

    if commit_code != 0:
        print("commit failed or nothing to commit")

    print("")
    print("Git push...")
    push_code = run(["git", "push", "-u", "origin", "main"])

    if push_code != 0:
        print("")
        print("GIT PUSH FAILED OR NEEDS AUTH")
        print("Manual command:")
        print(r'cd /d "D:\PYTHON\Forge Francaise"')
        print(r"scripts\git_push_patch3.cmd")

    print("")
    print("PATCH 3 DONE")
    print("Готовность проекта: примерно 45%")
    print("")
    print("Что добавлено:")
    print("- course API")
    print("- section page")
    print("- one-card lesson flow")
    print("- CardRenderer")
    print("- LessonTile")
    print("- pronunciation lessons")
    print("- nouns lessons")
    print("- verbs lessons")
    print("- phrasebook lessons")
    print("- more vulgar content")
    print("- git local identity fix")
    print("")
    print("Next patch will be step 4/6: real practice modes, review, progress scoring.")

if __name__ == "__main__":
    main()