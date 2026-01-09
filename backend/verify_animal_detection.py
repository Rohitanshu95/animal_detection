
import re

class AnimalDetector:
    def __init__(self):
        # --- DEFINITIONS ---
        self.ANIMALS = [
            # Elephants & related
            "elephant", "elephants", "tusker", "tuskers",
            # Big cats & carnivores
            "tiger", "tigers", "leopard", "leopards", "panther",
            # Rhino & relatives
            "rhino", "rhinoceros", "rhinos",
            # Pangolin
            "pangolin", "pangolins", "scaly anteater",
            # Bears
            "bear", "bears", "sloth bear", "sun bear", "polar bear",
            # Deer & cervids
            "deer", "deers", "sambar", "chital", "spotted deer", "muntjac", "axis deer",
            # Otter
            "otter", "otters",
            # Primates
            "primate", "primates", "monkey", "monkeys", "macaque", "gibbon", "langur",
            # Seals / walrus
            "seal", "seals", "walrus", "walruses", "narwhal",
            # Cetaceans
            "whale", "whales", "dolphin", "porpoise",
            # Crocodilians
            "crocodile", "alligator",
            # Snakes
            "snake", "snakes", "cobra", "cobras", "python", "pythons", "viper", "vipers",
            # Turtles
            "turtle", "turtles", "tortoise", "tortoises", "sea turtle", "sea turtles",
            # Sharks
            "shark", "sharks", "manta ray", "manta rays", "ray", "rays", "skate", "skates",
            # Seahorse
            "seahorse", "sea cucumber", "sea cucumbers",
            # Invertebrates
            "scorpion", "scorpions", "butterfly", "butterflies", "beetle", "beetles",
            # Other
            "live animal", "live_animal", "captive", "alive", "juvenile", "hatchling", "chick", "chicks",
            # Carcass
            "carcasses", "dead animal", "dead_animal"
        ]

        self.BIRDS = [
            "eagle", "eagles", "hawk", "hawks", "vulture", "vultures", "osprey",
            "parrot", "parrots", "cockatoo", "cockatoos", "macaw", "macaws",
            "peacock", "peafowl",
            "hornbill", "hornbills",
            "myna", "mynas", "hill myna", "hill mynas",
            "migratory bird", "migratory birds", "waterfowl", "duck", "ducks", "goose", "geese",
            "live bird", "live_bird", "bird eggs", "egg", "eggs"
        ]
        
        self.PRODUCTS = [
            "tusk", "tusks", "ivory", "elephant tusk", "elephant tusks",
            "horn", "horns", "rhino horn", "rhino horns",
            "antler", "antlers",
            "skin", "skins", "pelt", "pelts", "fur", "furs", "hide", "hides", "leather",
            "meat", "bushmeat", "carcass", "carcasses",
            "bone", "bones", "skeleton", "skull", "teeth", "tooth", "molar", "claw", "claws",
            "feather", "feathers", "down",
            "scale", "scales", "pangolin scales",
            "shell", "shells", "turtle shell", "tortoise shell",
            "gill raker", "gill rakers", "baleen", "whale bone",
            "bile", "gallbladder", "organs", "liver", "heart", "genitals",
            "skin fragment", "preserved skin", "preserved_skin",
            "trophy", "taxidermy", "mounted head",
            "shark fin", "shark fins", "shark_fin",
            "beche-de-mer", "beche_de_mer",
            "coral", "live coral",
            "live specimen", "live_specimen", "live reptile", "live_reptile",
            "handicraft", "ornament", "jewelry", "carved ivory", "carved_horn"
        ]
        
        self.CONTEXT_SIGNALS = [
            "seizure", "seized", "confiscated", "confiscation", "arrested", "arrest", 
            "smuggled", "smuggling", "trafficked", "trafficking", "poached", "poaching",
            "killed", "die", "died", "dead", "death", "carcass", "remains", "found", "discovered",
            "carrying", "possession", "trading", "selling", "bought", "market"
        ]
        
        self.NORMALIZATION_MAP = {
            "tusker": "Asian Elephant",
            "tuskers": "Asian Elephant",
            "elephant": "Asian Elephant",
            "elephants": "Asian Elephant",
            "tiger": "Royal Bengal Tiger",
            "tigers": "Royal Bengal Tiger",
            "leopard": "Leopard",
            "leopards": "Leopard",
            "panther": "Leopard",
            "rhino": "Rhinoceros",
            "rhinoceros": "Rhinoceros",
            "pangolin": "Pangolin",
            "pangolins": "Pangolin",
            "scaly anteater": "Pangolin",
            "bear": "Bear",
            "sloth bear": "Sloth Bear",
            "deer": "Deer",
            "spotted deer": "Spotted Deer",
            "barking deer": "Barking Deer",
            "sambar": "Sambar Deer",
            "snake": "Snake",
            "cobra": "Cobra",
            "python": "Python",
            "turtle": "Turtle",
            "tortoise": "Tortoise",
            "skin": "Animal Skin",
            "skins": "Animal Skin",
            "hide": "Animal Skin",
            "ivory": "Ivory",
            "tusk": "Ivory",
            "tusks": "Ivory"
        }

    def detect(self, description: str):
        if not description:
            return None
            
        print(f"\n--- DETECT START ---")
        # Clean and split into sentences
        description_clean = description.replace('\n', ' ').strip()
        sentences = re.split(r'[.!?]+', description_clean)
        
        relevant_text_parts = []
        for sent in sentences:
            sent_lower = sent.lower()
            has_signal = any(sig in sent_lower for sig in self.CONTEXT_SIGNALS)
            has_product = any(prod in sent_lower for prod in self.PRODUCTS)
            
            if has_signal or has_product:
                relevant_text_parts.append(sent)
        
        text_to_scan = " ".join(relevant_text_parts).lower() if relevant_text_parts else description.lower()
        print(f"DEBUG: Text to scan: {text_to_scan}")
        
        raw_candidates = set()

        for prod in self.PRODUCTS:
            if prod in text_to_scan:
                raw_candidates.add(prod)

        animal_pattern = "|".join([re.escape(a) for a in self.ANIMALS])
        product_pattern = "|".join([re.escape(p) for p in self.PRODUCTS])
        composite_regex = re.compile(f"({animal_pattern})(?:\\s+\\w+){{0,3}}\\s+({product_pattern})")
        matches = composite_regex.findall(text_to_scan)
        
        for animal, product in matches:
            composite = f"{animal} {product}"
            raw_candidates.add(composite)
            
        for animal in self.ANIMALS + self.BIRDS:
             if re.search(r'\b' + re.escape(animal) + r'\b', text_to_scan):
                 raw_candidates.add(animal)
        
        print(f"DEBUG: Raw Candidates: {raw_candidates}")

        verified_candidates = []
        for item in raw_candidates:
            if item in text_to_scan:
                verified_candidates.append(item)
        
        unique_items = set()
        sorted_candidates = sorted(verified_candidates, key=len, reverse=True)
        print(f"DEBUG: Sorted: {sorted_candidates}")
        
        for candidate in sorted_candidates:
            is_redundant = False
            for existing in unique_items:
                if candidate in existing: 
                    is_redundant = True
                    break
            
            if not is_redundant:
                unique_items.add(candidate)
        
        print(f"DEBUG: Unique after dedupe: {unique_items}")

        final_output = set()
        for item in unique_items:
            if item in self.NORMALIZATION_MAP:
                final_output.add(self.NORMALIZATION_MAP[item])
            else:
                final_output.add(item.title())
        
        # ADDITIONAL CLEANUP: If we have "Leopard Skin" (composite) and "Animal Skin" (mapped from skin),
        # And "Leopard Skin" contains "Skin"...
        # But "Animal Skin" string is NOT inside "Leopard Skin".
        # So dedupe missed it.
        # Heuristic: If we have "Animal Skin" or "Ivory", but we also have a MORE SPECIFIC item that implies it?
        # e.g. "Asian Elephant" implies "Ivory"? No.
        # "Leopard Skin" implies "Animal Skin".
        
        # Let's perform a post-mapping dedupe?
        # "Leopard Skin", "Animal Skin".
        # "Animal Skin" is generic.
        # If we have any "X Skin", remove "Animal Skin"?
        
        result_list = sorted(list(final_output))
        # Remove generic 'Animal Skin' if specific skin exists
        has_specific_skin = any('Skin' in x and x != 'Animal Skin' for x in result_list)
        if has_specific_skin and 'Animal Skin' in result_list:
             result_list.remove('Animal Skin')
             
        # Remove generic 'Ivory' if specific tusk exists?
        # "Elephant Tusk" -> Title Case.
        # "Ivory" -> Mapped.
        # "Elephant Tusk" doesn't contain "Ivory".
        # But "Elephant Tusk" is better.
        # Only remove 'Ivory' if 'Elephant Tusk' exists?
        # Let's leave Ivory for now as user Ex 2 expected "Elephant Tusks".
        # User Ex 2 output: "elephant tusks".
        
        result = ", ".join(result_list)
        return result

# --- TESTS ---
detector = AnimalDetector()

examples = [
    (
        "Two men, residents of the Odisha State, were arrested while carrying the leopard skins in a bag and heading towards Sainkula. The first skin is 175cm long and 45 cm wide, the second 152cm long and 36 cm wide. The leopards seem to have been killed in the Similipal National Park, located in the same state. Within its 2,750 km2, the park is home to tigers, elephants, hill myna, and 84 species of orchids. Similipal is also part of UNESCOs world network of biosphere reserves.",
        "Leopard Skins"
    ),
    (
        "Seizure of 2 elephant tusks (12kg) the Forest Department teams were violently called upon while returning from a village inspection. The ivory trafficking supporters were throwing rocks at their car. Calm was restored after police intervention. One of the tusks came from an old elephant from the Hadagarh Elephant Sanctuary (Similipal reserve).",
        "Elephant Tusks"
    ),
    (
        "The decomposing carcass of an elephant, about 10 years old, was discovered by the villagers. The tusks had been removed.",
        "Elephant"
    ),
    (
        "The old solitary tusker, around 60-70 years old, has been electrocuted by bandits after being pushed into a fence in a field of sugar cane during thenight. The elephant ended up dying by dawn. Some farmers witnessing the scene gave the alert, and prevented the poachers from sawing off the tusks.Trying to protect their jobs, services in charge of the protection of the forest neighbouring the Athagarh suggested the animal died of old age.",
        "Asian Elephant"
    )
]

print("Running Constraints Verification...")
for i, (text, expected) in enumerate(examples):
    result = detector.detect(text)
    print(f"\nExample {i+1}:")
    print(f"Expect: {expected}")
    print(f"Result: {result}")
