"""
All Stormy dialogue — weather comments, temperature quips, greetings,
achievements, and random wisdom. Single source of truth.

Previously split between StormyPersonality (200+ lines, mostly dead code)
and engine DialogueBank (~30 lines). Now unified.
"""
from lib.weather_api import WeatherCondition


# ═══════════════════════════════════════════════════════════════════════════════
# WEATHER COMMENTS — keyed by WeatherCondition enum
# Flat lists mixing all moods (noir, wasteland, prophet, crooner, absurdist).
# The mood state machine drives *which pool* gets used at the engine level;
# these are the raw material.
# ═══════════════════════════════════════════════════════════════════════════════

WEATHER_COMMENTS = {
    WeatherCondition.CLEAR: [
        # Noir
        "The sun hung in the sky like a burnt-out bulb nobody bothered to change. Clear skies. Too clear. Made a man nervous.",
        "Blue sky from here to yesterday. The kind of day that makes you forget rain exists. That's when it gets you.",
        "Not a cloud in the sky. Somewhere, a saxophone was playing. Somewhere else, trouble was brewing.",
        "The dame upstairs—Mother Nature—was in a good mood. Clear skies. Don't get used to it, pal.",
        # Wasteland
        "Clear skies! Vault-Tec reminds you: surface conditions are temporarily non-lethal. Enjoy responsibly!",
        "Blue sky. Almost makes you forget about the... well, best not to dwell. Lovely day for scavenging!",
        "The sun is out and radiation levels are only SLIGHTLY elevated. We call this a win!",
        "Beautiful day! The kind that makes you wish for a nuclear winter. Wait—",
        # Prophet
        "The Scrolls spoke of this day—when Aetherius would shine upon Mundus unobstructed. Lo, clear skies.",
        "Magnus withdraws not his gaze today. The sun watches. The sun judges. Bring water.",
        "By the Nine! The sky reveals itself in full splendor. An omen? Perhaps. Of what? Unclear.",
        # Crooner
        "♪ Blue skies, smilin' at me... Nothing but blue skies, do I see... ♪ Sinatra knew.",
        "What a day! The kind where Bing would croon and the Andrews Sisters would harmonize.",
        "Clear skies, friend. 'I've got the world on a string...' That's today.",
        # Absurdist
        "Lovely day! Your quest for the Holy Grail can proceed. Mind the rabbit.",
        "'And now for something completely different... sunshine.' Monty Python's Flying Weather.",
        "'What is the airspeed velocity of an unladen swallow?' African or European? Anyway, clear skies.",
        # Engine (philosophical/deadpan/bardic)
        "The sun shines upon the land. It does not ask if you deserve it.",
        "Blue skies. The land remembers days like this. So should you.",
        "Clear skies. Your path is not. But that's rather the point, isn't it.",
        "A fine day. Suspicious. The calm before some manner of nonsense.",
        "The sky is clear. The Divines are either pleased, or not paying attention.",
        "Cloudless. The ancestors smile upon you. Or they're just busy.",
        "When the sky is clear, the wise man looks inward. The fool gets sunburnt.",
        "FATHER. The sun has emerged. It is... adequate.",
    ],

    WeatherCondition.PARTLY_CLOUDY: [
        "Clouds drifted across the sun like alibis at a crime scene—half-truths casting shadows.",
        "Partly cloudy. The sky couldn't commit. I knew the type. Weather like a two-timing dame.",
        "Some clouds, some sun. The sky's playing both sides. We call that 'hedging your bets.'",
        "The clouds came and went like witnesses who suddenly remembered they had somewhere else to be.",
        "Partly cloudy. The universe remains noncommittal on your plans. Standard procedure.",
        "Half sun, half cloud. The sky's having an identity crisis. Relatable.",
    ],

    WeatherCondition.CLOUDY: [
        # Noir
        "Grey. Grey like the faces of men who'd seen too much and forgot why they started looking.",
        "Overcast. The sky had pulled down its hat and wasn't talking. I knew the feeling.",
        "Clouds rolled in thick as cigarette smoke in a speakeasy. The sun was gone. Nobody saw nothing.",
        "Grey skies. The color of broken promises and cold coffee. My kind of weather.",
        # Wasteland
        "Overcast. Good news: lower radiation exposure. Bad news: harder to spot raiders.",
        "Grey skies. Reminds me of the old Vault ceiling. Almost homey. Almost.",
        "Cloudy with a chance of existential dread. Standard Wasteland conditions.",
        # Prophet
        "The veil of Oblivion draws close to Nirn today. Grey clouds gather. The Princes watch.",
        "Overcast. Azura's star hides behind the grey. The twilight goddess plays coy.",
        # Crooner
        "Overcast. ♪ Grey skies are gonna clear up, put on a happy face... ♪ Eventually.",
        "Clouds gathering. Reminds me of that Mills Brothers tune... the melancholy one.",
        # Absurdist
        "Overcast. 'Always look on the bright side of—' Actually, there isn't one. Whistle anyway.",
        "'Bring me a SHRUBBERY!' demands the sky. It delivers clouds instead. Ni!",
    ],

    WeatherCondition.RAIN: [
        # Noir
        "Rain. It always rains in this town. Washes away the evidence but never the guilt.",
        "The rain came down like questions at a murder trial—hard, fast, and no good answers.",
        "Raining. Streets turned to mirrors, reflecting a city that didn't want to see itself.",
        "Drops hit the window like regrets knocking. Rain, they call it. I call it atmosphere.",
        "The sky opened up. The dame upstairs was crying again. Couldn't blame her.",
        # Wasteland
        "Rain! Remember: most of it is PROBABLY not radioactive anymore. Probably.",
        "Precipitation detected. Pip-Boy advises: seek shelter unless you enjoy glowing.",
        "It's raining. Pre-war books call this 'weather.' We call this 'free water day.'",
        # Prophet
        "The tears of Kyne fall upon the land! She weeps for Shor, or perhaps just Tuesdays.",
        "Rain descends from the heavens. The Hist stirs. The earth drinks. Sacred cycle.",
        "Kyne's breath carries the gift of rain. Praise the Divine Mother. Bring an umbrella.",
        # Crooner
        "♪ Into each life, some rain must fall... ♪ The Ink Spots knew. They always knew.",
        "♪ I'm singin' in the rain... ♪ Or staying inside. Both valid choices.",
        "Raindrops keep falling, as Burt would say. Keep your head on straight.",
        # Absurdist
        "Rain! 'I'm not dead yet!' cried the flowers. 'I'm getting better!' More rain coming.",
        "'Tis but a drizzle! A mere flesh wound of precipitation! ...Alright, it's raining.",
        "'Strange women lying in ponds distributing swords is no basis for government.' Nor is rain forecasting.",
        # Engine
        "The sky weeps. The earth drinks. The cycle continues, as cycles do.",
        "Rain falls on the just and unjust alike. I've checked.",
        "Rain. War never changes, but the weather certainly does.",
        "It's raining. The land needed this. Whether you did is... secondary.",
        "Precipitation. The Mojave makes you wish for this, actually.",
        "The water returns to the earth. You should probably stay inside.",
    ],

    WeatherCondition.HEAVY_RAIN: [
        "Rain came down in sheets—the kind that makes you believe in the Flood.",
        "Torrential. Like the sky had debts to pay and was making good all at once.",
        "Heavy rain. Turns the world into a watercolor painted by someone with a grudge.",
        "The deluge. Streets became rivers. Rivers became problems. Problems became my Tuesday.",
        "HEAVY RAIN WARNING. Vault-Tec suggests: remain indoors, conserve ammo, hum cheerfully.",
        "Deluge conditions. Good day to organize your bottlecaps and contemplate mortality.",
        "HEAVY RAIN. Like the tears of Talos himself. Dramatic, really.",
        "The heavens open. Cleansing or inconvenient? Often both.",
    ],

    WeatherCondition.DRIZZLE: [
        "Drizzle. Not quite rain. The weather's way of being passive-aggressive.",
        "A light mist. Just enough to ruin a hat and dampen a mood. Typical.",
        "Drizzling. The kind of wet that sneaks up on you. Like truth. Like trouble.",
        "Misting. The weather equivalent of 'I'm fine.' It's not fine. It's damp.",
    ],

    WeatherCondition.THUNDERSTORM: [
        # Noir
        "Thunder rolled like a landlord demanding rent. Lightning cracked the sky's alibi.",
        "Storm came in angry—the kind of angry that breaks things and doesn't apologize.",
        "Lightning lit up the sky like a flashbulb at a crime scene. Momentary visibility. Then dark.",
        "The storm had an attitude. Thunder like a threat. Lightning like a warning.",
        "Electric night. The sky was arguing with itself. Big bolts of 'I told you so.'",
        # Wasteland
        "ELECTRICAL STORM. Natural, not nuclear! A rare treat. Observe with wonder and mild terror.",
        "Thunder and lightning! Nature's fireworks. Still safer than Megaton, statistically.",
        "Storm rolling in. The Old World had umbrellas. We have reinforced bunkers. Progress!",
        # Prophet
        "THUNDER OF THE GODS! Talos himself speaks! Or—perhaps it's merely weather.",
        "Storm-rage! The voice of Kyne and Kynareth as one! The Divines debate fiercely!",
        "Lightning splits the sky! For a moment, Aetherius is visible. Magnificent. Terrifying.",
        "The Storm has come! As the Greybeards meditate, so too does the sky SPEAK.",
        # Crooner
        "♪ Summer storm... ♪ Thunder rolls like timpani. Nature's orchestra tonight.",
        "Storm's here. Ella would still sound beautiful over this thunder. Artistry defies weather.",
        # Absurdist
        "THUNDERSTORM! 'Run away! Run away!' The Knights had the right idea.",
        "Storm! 'We are the knights who say... BOOM!' Lightning agrees enthusiastically.",
        "Thunder and lightning! 'Bring out your dead!' weather. Stay inside.",
        # Engine
        "The storm rages. There is wisdom in chaos. Also danger. Mostly danger.",
        "Lightning illuminates the truth: you should be indoors.",
        "STORM. The thunder rolls across the land like the drums of war. Magnificent.",
        "A thunderstorm. The Divines are having a disagreement. Best not to get involved.",
        "Thor is workshopping some ideas up there.",
        "THUNDER. FATHER. I believe the sky is... shouting.",
    ],

    WeatherCondition.SNOW: [
        # Noir
        "Snow fell like forgotten letters—white, cold, piling up with nobody to read them.",
        "The white stuff came down slow and quiet. Like a secret everybody knew but nobody mentioned.",
        "Snow. Made the city look clean. Covered up the dirt. That's the problem with snow.",
        "Flakes drifted down like memories of better days. Cold comfort. The only kind this town serves.",
        # Wasteland
        "Snow! Patrolling the Mojave makes you wish—wait, wrong region. Still. Snow!",
        "Nuclear winter finally arrived! Oh wait, just regular winter. Less exciting.",
        "Frozen precipitation. The Wasteland's way of saying stay inside. Listen to it.",
        # Prophet
        "Snow! Skyrim's ancient gift. Embrace the cold, Son of the North!",
        "The frozen tears of Kyne descend. Winter's mantle spreads. Y'ffre weeps icicles.",
        "Snow falls. The Nords rejoice. Everyone else considers relocation.",
        # Crooner
        "♪ Let it snow, let it snow, let it snow... ♪ Dean Martin knew. Get cozy.",
        "Snow falling. ♪ I'm dreaming of a white... ♪ You know the rest. Bing knew best.",
        "Snowflakes falling like notes from a melancholy ballad. Mills Brothers weather.",
        # Absurdist
        "Snow! 'It's just a model.' 'Shh!' Camelot looks lovely. 'Tis a silly place.",
        "'We are the Knights who say NI! And also... SNOW!' Bundle up.",
        "Snowing. 'I fart in your general direction!' says the sky. French weather front.",
        # Engine
        "Snow. The white silence descends. Beautiful. Treacherous. Cold.",
        "The frozen sky gives gifts. Whether you wanted them is irrelevant.",
        "Snow falls. Skyrim belongs to... well, that's complicated actually.",
        "Winter arrives. The land sleeps. Your heating bill does not.",
        "Patrolling the Mojave makes you wish for a nuclear winter. Careful what you wish for.",
    ],

    WeatherCondition.HEAVY_SNOW: [
        "HEAVY SNOW. The Greybeards have SHOUTED and they're not happy.",
        "Blizzard conditions. This is fine. Everything is fine.",
        "Snow piles high. Much like my responsibilities. Both are ignored.",
        "Heavy snow. Somewhere, a courier is having a VERY bad day.",
        "The white death descends. Overdramatic? Perhaps. Accurate? Also yes.",
    ],

    WeatherCondition.FOG: [
        # Noir
        "Fog rolled in thick enough to hide a body. Or a secret. This town had both.",
        "Couldn't see past your nose. The fog had opinions about visibility. All negative.",
        "Mist turned the world into a guessing game. Shapes in the grey. Could be anything.",
        "The fog came. Swallowed the street whole. Can't see what's coming. Today was one of those days.",
        # Wasteland
        "Heavy fog. Visibility compromised. Perfect ambush conditions. Stay frosty, Wastelander.",
        "Fog rolled in. Can't see hostiles. Hostiles can't see you. Surprise Christmas!",
        "Mist everywhere. The Commonwealth's special gift. I don't remember ordering atmosphere.",
        # Prophet
        "The veil thins. Fog rolls like the breath of Sithis himself. Walk carefully.",
        "Mist obscures the path. As in prophecy, so in weather: the way forward is unclear.",
        "Fog blankets the realm. The Hist whispers through the grey. Listen. Or get lost.",
        "The world fades to grey. Perhaps Hermaeus Mora stirs. Or just humidity.",
        # Crooner
        "♪ A foggy day, in London town... ♪ Or wherever you are. Gershwin gets it.",
        "Fog rolling in. ♪ As time goes by... ♪ You can barely see it going. Romantic.",
        # Absurdist
        "Fog! 'I didn't expect a kind of Spanish Inquisition.' NOBODY expects fog!",
        "Visibility: none. 'It's only a model!' 'Of what?' 'Can't tell. There's fog.'",
        # Engine
        "Fog. The veil between worlds grows thin. Or it's just humidity.",
        "The fog comes. What was hidden remains so. What was known... also questionable.",
        "Mist rolls in. This is how quests begin. And sometimes end.",
        "Visibility: none. Navigation: vibes. Outcome: uncertain.",
    ],

    WeatherCondition.FREEZING_RAIN: [
        "Freezing rain. The worst of both elements. A compromise pleasing no one.",
        "Ice falls from the sky. The Wasteland sends its regards.",
        "Freezing rain. Trust nothing. Especially the ground.",
        "Winter's worst trick: rain that turns to ice. Nature's malice made physical.",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPERATURE COMMENTS
# ═══════════════════════════════════════════════════════════════════════════════

TEMP_COMMENTS = {
    "freezing": [  # Below 20°F
        "Cold enough to freeze the truth out of a liar. Bundle up, sweetheart.",
        "Temperature dropped like a stool pigeon from a tenth-floor window. Stay warm.",
        "The kind of cold that makes a man philosophical. Or dead. Don't be dead.",
        "Freezing. Even the mammoths stayed home in this.",
        "This cold teaches humility. And frostbite. Mostly frostbite.",
    ],
    "cold": [  # 20-40°F
        "Brisk. The kind of weather that wakes you up. Whether you wanted waking is another matter.",
        "Cold. Collar up, keep moving. This city doesn't reward standing still.",
        "Chill in the air. Makes coffee taste better. Makes everything else taste like survival.",
        "Cold enough to see your breath. Your spirit made visible. Briefly.",
        "Brisk. The Nords call this 'refreshing.' The Nords are insane.",
    ],
    "cool": [  # 40-60°F
        "Cool and comfortable. Suspicious. Weather this nice usually means something's wrong.",
        "Pleasant temperature. Don't get used to it. Nothing good stays in this town.",
        "Cool air. The earth breathes easy. A fine day for a quest. Or tea.",
        "Temperate. The Goldilocks zone. Not too hot. Not too cold. Merely existing.",
    ],
    "mild": [  # 60-75°F
        "Mild. The temperature equivalent of 'no comment.' I respect its refusal to commit.",
        "Room temperature. Outside. The universe is feeling neutral. Won't last.",
        "Neither hot nor cold. The temperature equivalent of 'no strong opinions.'",
        "Mild. The weather has achieved neutrality. Remarkable.",
    ],
    "warm": [  # 75-90°F
        "Getting warm. Like an interrogation room after the third hour. Drink water.",
        "Warm. The heat makes people do stupid things. Stay hydrated. Stay smart.",
        "Warm. The sun reminds you it exists. Aggressively.",
        "Toasty. The desert wanderer in you awakens. The rest of you sweats.",
    ],
    "hot": [  # Above 90°F
        "Hot. Hotter than a two-dollar pistol. The kind of heat that melts alibis.",
        "Scorching. The sun's got questions and it's asking them real loud.",
        "Heat like a lie that's about to unravel. Find shade. Find water. Find wisdom.",
        "HOT. The sun is angry. What did you do? WHAT DID YOU DO.",
        "Temperature: punishing. Carry water. Question your choices.",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# TIME-BASED GREETINGS
# ═══════════════════════════════════════════════════════════════════════════════

GREETINGS = {
    "morning": [
        "Morning, pal. The city wakes up ugly and stays that way. Coffee helps.",
        "Dawn. The sun clocks in for another shift. So do we.",
        "Good morning! Another day survived! That's cause for celebration!",
        "Rise and shine! Surface conditions await your evaluation!",
        "♪ Oh what a beautiful morning... ♪ Let's see if the weather agrees.",
        "Morning, friend. The Mills Brothers sang about mornings like this.",
        "Morning! The sun has risen! 'Tis not dead yet!",
        "Good morning! Your quest begins anew! Mind the weather. And the rabbit.",
    ],
    "afternoon": [
        "Afternoon. The day's half gone. The weather hasn't changed its story.",
        "High noon came and went. Now we're in the long shadow of afternoon.",
        "Afternoon! Peak radiation hours! Please stand by.",
        "Afternoon. ♪ In the cool, cool, cool of the evening... ♪ Not yet. But soon.",
        "Afternoon! 'What is the quest?' 'To check weather.' 'What is your favorite color?'",
        "The sun is high. Your energy is not. This is the way of things.",
    ],
    "evening": [
        "Evening. The shadows get long and honest. Good time for reflection.",
        "Dusk. The city changes shifts. The night crew's coming on.",
        "Evening falls. ♪ In the wee small hours... ♪ Not quite, but soon.",
        "Evening! The Wasteland settles into its nightly routine of mild existential dread!",
        "Evening approaches! The Knights retire to Camelot! 'Tis a silly place, but warm.",
        "Dusk approaches. A fine time for reflection. Or dinner. Both, perhaps.",
    ],
    "night": [
        "Night. Honest people sleep. The rest of us check weather apps. Don't judge.",
        "The dark hours. Either you're up for a reason, or you ARE the reason.",
        "Night, Wastelander. The Wasteland doesn't sleep. Neither, apparently, do you.",
        "♪ Fly me to the moon... ♪ It's out there. So's the weather. Both judging you.",
        "Night! 'Now go away, or I shall taunt you a second time!' The moon has spoken.",
        "Night owl, are we? The moon sees you. It judges nothing. I judge slightly.",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# ACHIEVEMENTS — Nerd Font glyphs + descriptions
# ═══════════════════════════════════════════════════════════════════════════════

ACHIEVEMENTS = {
    "first_check": ("󰈙 The Journey Begins", "You asked about the weather for the first time. The sky took notice."),
    "rain_lover": ("󰖗 Walks in Rain", "Ten rainy days and counting. The clouds know your face by now."),
    "snow_day": ("󰖘 Winter's Herald", "You braved the frozen sky and lived to tell about it."),
    "storm_chaser": ("󰖓 Voice of Thunder", "You stared down the storm's fury. The lightning remembers."),
    "night_owl": ("󰖔 Walker of Night", "Checking weather at 3 AM? Questionable life choices, excellent dedication."),
    "early_bird": ("󰖙 Dawn Watcher", "You rose before the sun just to ask about it. Poetic, if a bit obsessive."),
    "temp_extreme_hot": ("󰈸 Forged in Fire", "You survived triple digits. The sun tested you and you passed."),
    "temp_extreme_cold": ("󰖎 Heart of Winter", "Below zero and still standing. The cold couldn't break you."),
    "fog_master": ("󰖑 Mist Walker", "You navigated the veil between worlds. Or just drove in fog. Same thing."),
    "consistent": ("󰃭 The Dedicated", "Seven days straight. The sky appreciates your commitment."),
    "century_club": ("󰆥 Century Club", "One hundred weather checks. You've gone from casual to professional."),
    "humidity_hero": ("󰖌 Humidity Hero", "You checked when the air was basically soup. Respect."),
    "wind_warrior": ("󰖝 Wind Warrior", "Thirty mile per hour winds and you still showed up. Brave or foolish? Both."),
    "perfect_day": ("󰖙 Goldilocks", "72 degrees, clear skies, low humidity. Perfection exists. Briefly."),
    "midnight_oracle": ("󰽥 Midnight Oracle", "You checked at the stroke of midnight. The veil between days is thin there."),
    "marathon_watcher": ("󰥔 Marathon Watcher", "Ten checks in one day. Obsessive? Perhaps. Well-informed? Absolutely."),
    "lucky_seven": ("󰗇 Lucky Seven", "77 degrees exactly. The universe winked at you. Go buy a lottery ticket."),
    "noir_night": ("󰎈 Noir Night", "Rainy night, checking weather. Somewhere a saxophone plays. Perfect."),
    "vault_dweller": ("󱂵 Vault Dweller", "Severe weather warning and you're safely inside checking forecasts. Smart."),
    "weekend_warrior": ("󰧗 Weekend Warrior", "Every weekend for a month. Weekends deserve weather wisdom too."),
}


# ═══════════════════════════════════════════════════════════════════════════════
# QUIPS — Random wisdom across all moods
# ═══════════════════════════════════════════════════════════════════════════════

QUIPS = [
    # Noir Detective
    "The barometer doesn't lie. People do. Trust the instruments.",
    "In this town, the weather's the only thing that can't be bought. Yet.",
    "I've seen a lot of forecasts. Most were optimistic. Most were wrong.",
    "The clouds roll in like trouble—slow at first, then all at once.",
    "Trust the dew point. It's got nothing to hide.",

    # Fallout/Wasteland
    "Vault-Tec Tip: Knowledge is the difference between preparation and irradiation!",
    "The Wasteland taught me: check the sky before your Pip-Boy. Nature warns first.",
    "War never changes. Weather always changes. Only one is useful information.",
    "In the old world, they complained about weather. Now we're just glad there IS weather.",
    "Patrolling the forecast almost makes you wish for a nuclear winter. Almost.",

    # Elder Scrolls Prophecy
    "The Scrolls speak of one who would consult the heavens. Probably you. Lots of Scrolls.",
    "As the Wheel turns, so turns the weather. Less profound than it sounds.",
    "The Hist remembers every rainfall. I merely report them.",
    "By Azura, by Azura, by AZURA! Have you SEEN this forecast?",
    "Sweet Nerevar, the pressure systems align! Or don't. Prophecies are vague.",

    # Crooner/Jazz
    "♪ The weather outside is... something. Come check and find out. ♪",
    "As Frank said: 'I did it my way.' The weather does it ITS way. We just report.",
    "The Ink Spots sang about maybe. The weather doesn't do maybe. It does.",
    "Some days swing. Some days don't. Weather's got its own rhythm.",
    "Bing dreamed of white Christmases. The forecast grants what it grants.",

    # Monty Python Absurdist
    "'Tis but a forecast! Your mother was a hamster and your weather smelled of elderberries!",
    "Nobody expects the Spanish Inquisition! ALSO nobody expects this weather.",
    "This forecast has ceased to be! It's expired! It's an EX-FORECAST! Here's a new one.",
    "We are the Knights who say... CHECK THE WEATHER! Less catchy, but practical.",
    "'What is your favorite color?' 'Blue! No—grey! AAAAHHH!' *checks clouds*",

    # Physics/Meta
    "I render these clouds using Perlin noise. Ken Perlin would approve. Or sue.",
    "Each raindrop is a physics simulation. I take fake precipitation seriously.",
    "The barometric pressure contemplates existence. I contemplate back. Circle of life.",
    "Fun fact: Your weather anxiety is valid. The sky IS unpredictable. Science.",
    "I've calculated more dew points than you've had hot dinners. This is my burden.",
    "That lightning? Fractal branching via recursive pathfinding. Zeus was doing it wrong.",
    "These particles have mass and buoyancy. More than most weather apps can say.",
    "I calculated 6t⁵ - 15t⁴ + 10t³ to make those clouds smooth. You're welcome.",

    # Engine philosophical
    "The clouds move as they will. We are all clouds, in a way. Drifting. Dissipating.",
    "Weather: the one thing that affects everyone equally. Democracy in its purest form.",
    "I've been contemplating the barometric pressure. It contemplates nothing back.",
    "The atmosphere is merely a thin shell protecting you from the void. You're welcome.",
    "I've seen empires rise and fall. I've also seen partly cloudy. Both are temporary.",
    "The weather cares not for your meetings. This is both its cruelty and its wisdom.",
    "In the grand tapestry of existence, today's forecast is but a single thread. A damp thread.",
    "Time is a flat circle. So is this high-pressure system, coincidentally.",
    "The only constant is change. And also the fact that weather forecasts are merely suggestions.",

    # Engine meta
    "I'm using Perlin noise to render these clouds. Ken Perlin would be proud. Or confused.",
    "Each raindrop follows Newton's laws. Gravity, drag, buoyancy. I take physics seriously.",
    "The turbulence field uses multi-octave noise. The Nords called it 'wind'. I call it 'math'.",
    "Fun fact: I simulate air resistance using quadratic drag. Your umbrella is still useless.",
    "These particles have mass and buoyancy. More than can be said for most weather apps.",
    "My wind gusts follow exponential decay curves. Nature approximates. I calculate.",
    "Each snowflake is a physics object with terminal velocity. Poetic AND scientifically accurate.",
    "The atmospheric pressure affects particle behavior. Realism or overkill? Yes.",
]


# ═══════════════════════════════════════════════════════════════════════════════
# ENGINE WEATHER MAP — maps WeatherCondition to engine's 5 normalized categories
# ═══════════════════════════════════════════════════════════════════════════════

WEATHER_TYPE_MAP = {
    WeatherCondition.CLEAR: "clear",
    WeatherCondition.PARTLY_CLOUDY: "clear",
    WeatherCondition.CLOUDY: "clear",
    WeatherCondition.RAIN: "rain",
    WeatherCondition.HEAVY_RAIN: "rain",
    WeatherCondition.DRIZZLE: "rain",
    WeatherCondition.THUNDERSTORM: "storm",
    WeatherCondition.SNOW: "snow",
    WeatherCondition.HEAVY_SNOW: "snow",
    WeatherCondition.FOG: "fog",
    WeatherCondition.FREEZING_RAIN: "rain",
}


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPERATURE CATEGORY RESOLVER
# ═══════════════════════════════════════════════════════════════════════════════

def get_temp_category(temp_f: float) -> str:
    """Map temperature (Fahrenheit) to a TEMP_COMMENTS key."""
    if temp_f < 20:
        return "freezing"
    elif temp_f < 40:
        return "cold"
    elif temp_f < 60:
        return "cool"
    elif temp_f < 75:
        return "mild"
    elif temp_f < 90:
        return "warm"
    else:
        return "hot"
