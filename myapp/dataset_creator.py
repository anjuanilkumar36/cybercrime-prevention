# dataset_creator.py
import pandas as pd
import numpy as np
import random


class ToxicDatasetGenerator:
    def __init__(self):
        self.normal_messages = self._load_normal_messages()
        self.toxic_messages = self._load_toxic_messages()

    def _load_normal_messages(self):
        """Generate normal/neutral messages in multiple languages"""
        return {
            'english': [
                "Hello, good morning everyone!", "Have a wonderful day ahead",
                "Thank you for your help", "Great work on the project",
                "I appreciate your efforts", "Let's work together on this",
                "That's an interesting perspective", "Thanks for sharing your thoughts",
                "Looking forward to our meeting", "Have a productive day",
                "Nice to meet you all", "Let's collaborate on this task",
                "I agree with your point", "Well done everyone",
                "Keep up the good work", "Thanks for the update",
                "I understand your concern", "Let me know if you need help",
                "That's a good suggestion", "I'll get back to you soon",
                "Good job team", "Appreciate your support",
                "Let's discuss this further", "Thanks for your time",
                "Have a great weekend", "Looking good everyone",
                "I like your idea", "Let's move forward with this",
                "Thanks for the information", "I'll take care of it"
            ],
            'malayalam': [
                "സുപ്രഭാതം എല്ലാവർക്കും", "ഇന്നത്തെ ദിവസം ശുഭമായിരിക്കട്ടെ",
                "നിങ്ങളുടെ സഹായത്തിന് നന്ദി", "പ്രോജക്റ്റിൽ നല്ല പ്രവർത്തനം",
                "നിങ്ങളുടെ പ്രയത്നങ്ങളെ ഞാൻ വിലമതിക്കുന്നു", "നമുക്ക് ഒരുമിച്ച് പ്രവർത്തിക്കാം",
                "അതൊരു രസകരമായ കാഴ്ചപ്പാടാണ്", "നിങ്ങളുടെ ചിന്തകൾ പങ്കിട്ടതിന് നന്ദി",
                "ഞങ്ങളുടെ മീറ്റിംഗിനായി കാത്തിരിക്കുന്നു", "ഉൽപാദനപരമായ ഒരു ദിവസം ആശംസിക്കുന്നു",
                "നിങ്ങളെല്ലാം കണ്ടതിൽ സന്തോഷമുണ്ട്", "ഈ ജോലിയിൽ നമുക്ക് സഹകരിക്കാം",
                "നിങ്ങളുടെ വാദം ഞാൻ അംഗീകരിക്കുന്നു", "എല്ലാവർക്കും നന്നായി",
                "നല്ല പ്രവർത്തനം തുടരുക", "അപ്ഡേറ്റിന് നന്ദി",
                "നിങ്ങളുടെ ആശങ്ക ഞാൻ മനസ്സിലാക്കുന്നു", "സഹായം ആവശ്യമെങ്കിൽ എന്നോട് പറയുക",
                "അതൊരു നല്ല നിർദ്ദേശമാണ്", "ഞാൻ വേഗം തിരികെ വരുന്നു",
                "നല്ല ജോലി ടീം", "നിങ്ങളുടെ പിന്തുണയ്ക്ക് നന്ദി",
                "നമുക്ക് ഇത് കൂടുതൽ ചർച്ച ചെയ്യാം", "സമയം നൽകിയതിന് നന്ദി",
                "നല്ല വാരാന്ത്യം ആശംസിക്കുന്നു", "എല്ലാവരും നന്നായി കാണപ്പെടുന്നു",
                "നിങ്ങളുടെ ആശയം എനിക്ക് ഇഷ്ടമായി", "നമുക്ക് ഇത് മുന്നോട്ട് കൊണ്ടുപോകാം",
                "വിവരങ്ങൾ നൽകിയതിന് നന്ദി", "ഞാൻ ഇത് കൈകാര്യം ചെയ്യുന്നു"
            ],
            'tamil': [
                "வணக்கம் அனைவருக்கும்", "இன்றைய தினம் மிக நல்லதாக அமையட்டும்",
                "உங்கள் உதவிக்கு நன்றி", "திட்டத்தில் நல்ல வேலை",
                "உங்கள் முயற்சிகளை நான் பாராட்டுகிறேன்", "நாம் ஒன்றாக வேலை செய்வோம்",
                "அது ஒரு சுவாரஸ்யமான பார்வை", "உங்கள் எண்ணங்களைப் பகிர்ந்தமைக்கு நன்றி",
                "எங்கள் கூட்டத்திற்காக காத்திருக்கிறேன்", "உற்பத்தி நாள் வாழ்த்துக்கள்",
                "நீங்கள் அனைவரையும் பார்த்ததில் மகிழ்ச்சி", "இந்த பணியில் நாம் ஒத்துழைப்போம்",
                "உங்கள் வாதத்தை ஏற்கிறேன்", "அனைவருக்கும் நல்லது",
                "நல்ல வேலையைத் தொடருங்கள்", "புதுப்பித்தலுக்கு நன்றி",
                "உங்கள் கவலையை புரிந்து கொள்கிறேன்", "உதவி தேவைப்பட்டால் எனக்குத் தெரியப்படுத்துங்கள்",
                "அது ஒரு நல்ல யோசனை", "நான் விரைவில் திரும்பி வருகிறேன்",
                "நல்ல வேலை குழு", "உங்கள் ஆதரவைப் பாராட்டுகிறேன்",
                "இதை மேலும் விவாதிப்போம்", "உங்கள் நேரத்திற்கு நன்றி",
                "நல்ல வார இறுதி நாட்கள்", "அனைவரும் நன்றாக இருக்கிறார்கள்",
                "உங்கள் யோசனை எனக்கு பிடித்திருக்கிறது", "இதைத் தொடர்ந்து செல்வோம்",
                "தகவலுக்கு நன்றி", "நான் இதை கவனித்துக்கொள்கிறேன்"
            ],
            'hindi': [
                "नमस्ते सभी को सुप्रभात", "आपका दिन शुभ हो",
                "आपकी सहायता के लिए धन्यवाद", "प्रोजेक्ट पर अच्छा काम",
                "मैं आपके प्रयासों की सराहना करता हूं", "आइए मिलकर काम करते हैं",
                "यह एक दिलचस्प दृष्टिकोण है", "अपने विचार साझा करने के लिए धन्यवाद",
                "हमारी मीटिंग का इंतजार है", "उत्पादक दिन की शुभकामनाएं",
                "आप सभी से मिलकर अच्छा लगा", "इस कार्य में सहयोग करते हैं",
                "मैं आपकी बात से सहमत हूं", "सभी को बहुत बढ़िया",
                "अच्छा काम जारी रखें", "अपडेट के लिए धन्यवाद",
                "मैं आपकी चिंता समझता हूं", "यदि आपको सहायता चाहिए तो मुझे बताएं",
                "यह एक अच्छा सुझाव है", "मैं जल्द ही वापस आऊंगा",
                "अच्छा काम टीम", "आपके समर्थन की सराहना करते हैं",
                "आइए इस पर और चर्चा करें", "आपके समय के लिए धन्यवाद",
                "शुभ सप्ताहांत", "सभी अच्छे लग रहे हैं",
                "मुझे आपका विचार पसंद आया", "आइए इसे आगे बढ़ाएं",
                "जानकारी के लिए धन्यवाद", "मैं इसका ध्यान रखूंगा"
            ]
        }

    def _load_toxic_messages(self):
        """Generate toxic messages in multiple languages and mixed variations"""
        return {
            # Pure Language Toxic Messages
            'malayalam_pure': [
                "പോയിക്കോ ഇവിടെനിന്ന്", "നീ ഒരു മണ്ടൻ ആണ്", "വെറുക്കപ്പെട്ട ആള്",
                "പൊയ്ക്കൊള്ളു മണ്ടാ", "തെണ്ടി പോയി", "മോശക്കാരൻ", "പാവം",
                "നിസ്സാരൻ", "ചീച്ച", "നായ്", "പട്ടി", "പൊട്ടി", "നിന്റെ അമ്മ",
                "പുള്ളി മൈരൻ", "കോളറൻ", "വിഡ്ഢി", "ബുദ്ധിശാലി", "മൈരം",
                "പൊട്ടൻ", "കുഴപ്പക്കാരൻ", "പോയി ജോലി നോക്ക്", "വേല പോകട്ടെ",
                "നിന്റെ തലയിൽ കയറി", "പോയി വെള്ളം കുടി", "നീ പോയി ചാവ്",
                "മണ്ടനേ പോയി", "പൊട്ടാ പോയി", "കുഴപ്പമുള്ളവൻ", "തിരിച്ചുപോകാൻ"
            ],
            'tamil_pure': [
                "போடா முட்டாள்", "பொருக்கி பயலே", "ஊத்தி போடா", "புண்ட அவன்",
                "மடையன் போடா", "கேவலமானவன்", "திமிர் பிடித்தவன்", "நிமிண்டு",
                "மொக்க பய", "ஓட்டை பய", "நாய் பய", "புண்ட கழுதை", "சேலை",
                "தள்ளிப் போடா", "கழுதை மகன்", "பயலுவது", "முட்டாள் பய",
                "கேவலம்", "அசிங்கம்", "கீழ்த்தரம்", "போய் வேலை பார்", "வேலை போகட்டும்",
                "உன் தலையில் ஏறு", "போய் தண்ணீர் குடி", "நீ போய் சாக",
                "முட்டாளே போய்", "ஓட்டை போய்", "கெட்டவன்", "திரும்பிப் போ"
            ],
            'hindi_pure': [
                "चल भाग यहाँ से", "तू बेवकूफ है", "गधे कहीं के", "हरामी आदमी",
                "भोसड़ी वाला", "कमीना", "चूतिया", "मूर्ख", "निकम्मा", "अयोग्य",
                "बेकार", "असफल", "लंगड़ा", "अंधा", "बहरा", "गूंगा", "पागल",
                "सुअर", "कुत्ता", "गंदगी", "जा काम देख", "काम चला जाए",
                "तेरे सिर पर चढ़ जाऊं", "जा पानी पी", "तू जा के मर",
                "मूर्ख जा", "छेद जा", "बुरा आदमी", "वापस जा"
            ],
            'english_pure': [
                "You are stupid", "Get lost idiot", "You useless moron",
                "Go to hell", "Shut up loser", "You dumb fool", "Waste fellow",
                "Bloody idiot", "You disgusting man", "You trash",
                "You are garbage", "Die you fool", "Kill yourself",
                "You're worthless", "You pathetic loser", "You fool stop talking",
                "You dumb head", "You're a total waste", "You disgusting waste",
                "You're such a fool", "Go away you fool", "Get out of here",
                "You're a failure", "You good for nothing", "You piece of trash",
                "You're horrible", "You make me sick", "You're terrible",
                "I hate you", "You're the worst"
            ],

            # Mixed Language Toxic Messages (Manglish, Hinglish, Tanglish)
            'manglish': [
                "poyi da myre", "poda myre", "thendi mone", "potti mon",
                "myre poyi", "punda da", "muttal poi", "adi da",
                "poyikko myre", "mon myre", "poyi vayasu", "poyi thirinu",
                "myre pokku", "punda pokku", "thendi pokku", "mone pokku",
                "poyi pani nokku", "vela pokade", "poyi oombu", "myre oombu",
                "poyi chavu", "poda mone", "thendi poi", "punda mone",
                "myre adi", "mon poyi", "poyi vellam kudiku", "myre vellam"
            ],
            'hinglish': [
                "bevkoof mon", "gadha mon", "pagal myre", "chup myre",
                "teri maa myre", "harami mone", "kamine mon", "chutiya mon",
                "bhosdi myre", "lund mone", "randi mon", "gandu myre",
                "bevkoof ja", "gadha ho kya", "pagal hai kya", "chup kar myre",
                "teri maa ki", "harami kamine", "kutte mon", "suar myre",
                "ja be mon", "chutiya ho kya", "randi ka bacha", "gandu ja",
                "bevkoof nikamma", "gadha admi", "pagal insaan", "kamine aadmi"
            ],
            'tanglish': [
                "poda loosu", "myre da", "thendi da", "punda da",
                "poyi muttal", "mon loosu", "myre muttal", "punda muttal",
                "loosu poi", "muttal da", "poyi da loosu", "poda myre",
                "kevalam myre", "thendi da", "punda loosu", "myre kevalam",
                "poyi saavu", "poda oombu", "myre oombu", "punda oombu",
                "poyi vayasu da", "poda payale", "thendi paya", "punda paya",
                "myre othi", "loosu po", "muttal po", "punda po"
            ],

            # Multi-language mixed toxic
            'multilingual_mixed': [
                "poyi da you idiot", "stupid myre", "idiot mone", "fool myre",
                "moron da", "loser myre", "garbage mon", "trash mone",
                "you bevkoof", "you gadha", "you pagal", "you chutiya",
                "poyi da stupid", "poda idiot", "thendi fool", "punda moron",
                "myre loser", "mon garbage", "mone trash", "da waste",
                "go away myre", "get lost da", "shut up mon", "die poi",
                "kill yourself poyi", "you're worthless myre", "you trash mon",
                "you garbage da", "you fool poi", "you idiot pokku"
            ]
        }

    def generate_dataset(self, num_samples=2000):
        """Generate a balanced dataset of normal and toxic messages"""
        dataset = []

        # Calculate samples per category
        normal_samples = num_samples // 2
        toxic_samples = num_samples // 2

        # Generate normal messages
        normal_count = 0
        languages = list(self.normal_messages.keys())

        while normal_count < normal_samples:
            for lang in languages:
                messages = self.normal_messages[lang]
                for message in messages:
                    if normal_count >= normal_samples:
                        break
                    dataset.append({
                        'message': message,
                        'label': 0,
                        'language': lang,
                        'type': 'normal'
                    })
                    normal_count += 1
                    if normal_count >= normal_samples:
                        break

        # Generate toxic messages
        toxic_count = 0
        toxic_categories = [
            'malayalam_pure', 'tamil_pure', 'hindi_pure', 'english_pure',
            'manglish', 'hinglish', 'tanglish', 'multilingual_mixed'
        ]

        while toxic_count < toxic_samples:
            for category in toxic_categories:
                messages = self.toxic_messages[category]
                for message in messages:
                    if toxic_count >= toxic_samples:
                        break
                    lang_type = category.split('_')[0] if '_' in category else category
                    dataset.append({
                        'message': message,
                        'label': 1,
                        'language': lang_type,
                        'type': 'toxic'
                    })
                    toxic_count += 1
                    if toxic_count >= toxic_samples:
                        break

        # Shuffle the dataset
        random.shuffle(dataset)

        return pd.DataFrame(dataset)

    def save_dataset(self, filename='multilingual_toxic_dataset.csv', num_samples=2000):
        """Generate and save the dataset to CSV"""
        df = self.generate_dataset(num_samples)
        df.to_csv(filename, index=False, encoding='utf-8')

        # Print dataset statistics
        print(f"✅ Dataset saved to: {filename}")
        print(f"📊 Total samples: {len(df)}")
        print(f"📈 Label distribution:")
        print(df['label'].value_counts())
        print(f"🌍 Language distribution:")
        print(df['language'].value_counts())
        print(f"📝 Type distribution:")
        print(df['type'].value_counts())

        # Show sample messages
        print(f"\n📋 Sample messages from dataset:")
        print("Normal messages:")
        for msg in df[df['label'] == 0]['message'].head(3):
            print(f"  - {msg}")
        print("Toxic messages:")
        for msg in df[df['label'] == 1]['message'].head(3):
            print(f"  - {msg}")

        return df

    def analyze_dataset(self, df):
        """Analyze and display dataset statistics"""
        print(f"\n📊 DATASET ANALYSIS")
        print(f"==================")
        print(f"Total samples: {len(df)}")
        print(f"Normal messages: {len(df[df['label'] == 0])}")
        print(f"Toxic messages: {len(df[df['label'] == 1])}")

        print(f"\n🌍 Language Distribution:")
        lang_stats = df['language'].value_counts()
        for lang, count in lang_stats.items():
            percentage = (count / len(df)) * 100
            print(f"  {lang}: {count} samples ({percentage:.1f}%)")

        print(f"\n📝 Sample from each language category:")
        for lang in df['language'].unique():
            samples = df[df['language'] == lang].head(2)
            print(f"\n{lang.upper()}:")
            for _, row in samples.iterrows():
                toxicity = "🚨 TOXIC" if row['label'] == 1 else "✅ NORMAL"
                print(f"  {toxicity}: {row['message']}")


# Main execution
if __name__ == "__main__":
    print("=== MULTILINGUAL TOXIC COMMENT DATASET GENERATOR ===")
    print("Creating comprehensive dataset for Indian languages...")

    # Initialize generator
    generator = ToxicDatasetGenerator()

    # Generate and save dataset
    dataset_path = 'multilingual_toxic_dataset.csv'
    df = generator.save_dataset(dataset_path, num_samples=2000)

    # Analyze dataset
    generator.analyze_dataset(df)

    print(f"\n🎉 Dataset creation completed!")
    print(f"📁 File saved as: {dataset_path}")
    print(f"💾 You can now use this dataset path in your main toxic detection code.")