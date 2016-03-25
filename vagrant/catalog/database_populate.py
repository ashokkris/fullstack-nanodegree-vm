# Credits: Descriptions for sports equipment below come from Wikipedia
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, User, CategoryItem

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

user = User(name = "Ashok Srinivasan", email = "ashokkrishnans@gmail.com")
session.add(user)

dummy = User(name = "Joe Dummy", email = "joe.dummy@gmail.com")
session.add(dummy)

session.commit()


cricket = Category(title = "Cricket")
session.add(cricket)
rock_climbing = Category(title = "Rock Climbing")
session.add(rock_climbing)
soccer = Category(title = "Soccer")
session.add(soccer)
hang_gliding = Category(title = "Hang Gliding")
session.add(hang_gliding)
skiing = Category(title = "Skiing")
session.add(skiing)
skating = Category(title = "Roller Skating")
session.add(skating)
water_polo = Category(title = "Water Polo")
session.add(water_polo)
basketball = Category(title = "Basketball")
session.add(basketball)
beach_tennis = Category(title = "Beach Tennis")
session.add(beach_tennis)
session.commit()

description = ("A cricket ball is a hard, solid ball used to play the game. "
	"A cricket ball consists of cork covered by leather, and manufacture is "
	"regulated by cricket law at first class level. The manipulation of a "
	"cricket ball, through employment of its various physical properties, is "
	"a staple component of bowling and dismissing batsmen.")
ball = CategoryItem(title = "Cricket Ball", 
	description = description, category = cricket, user = user,
	image = "cricket_ball.png")
session.add(ball)

description = ("The blade of a cricket bat is a wooden block that is "
	"generally flat on the striking face and with a ridge on the reverse "
	"(back) which concentrates wood in the middle where the ball is generally "
	"hit. The bat is traditionally made from willow wood, specifically from a "
	"variety of White Willow called Cricket Bat Willow.")
bat = CategoryItem(title = "Cricket Bat", 
	description = description, category = cricket, user = user,
	image = "cricket_bat.png")
session.add(bat)

description = ("The stumps are three vertical posts which support two "
	"bails.The stumps and bails are usually made of wood, most commonly ash, "
	"and together form a wicket at each end of the pitch.")
stumps = CategoryItem(title = "Stumps", 
	description = description, category = cricket, user = user,
	image = "cricket_stumps.png")
session.add(stumps)

description = ("In the sport of cricket, a bail is one of the two smaller "
	"sticks placed on top of the three stumps to form a wicket. The bails are "
	"used to determine when the wicket is broken, which in turn is one of the "
	"critical factors in determining whether a batsman is out bowled, "
	"stumped, run out or hit wicket.")
bail = CategoryItem(title = "Bail", 
	description = description, category = cricket, user = user,
	image = "cricket_bail.png")
session.add(bail)

description = ("Leg Pads fall into two types, batting pads and "
	"wicket-keeper's pads. In Test and first-class cricket, the pads are "
	"white, while in limited overs cricket they may be coloured. "
	"Pads protect the player's shins, knees and the lower thigh against "
	"impact from the cricket ball. The wicket-keeping pads are slightly "
	"different from the batsmen's.")
pads = CategoryItem(title = "Leg Pads", 
	description = description, category = cricket, user = user,
	image = "cricket_pads.png")
session.add(pads)

description = ("Batting gloves typically consist of a leather palm and "
	"back made of nylon or another synthetic fabric. The glove covers both "
	"hands of a batsman, providing comfort, prevention of blisters, warmth, "
	"improved grip, and shock absorption when hitting the ball. "
	"These gloves are thickly padded above the fingers and on the thumb of "
	"batsman's hand, to protect against impact from the ball as it is bowled")
b_gloves = CategoryItem(title = "Batting Gloves", 
	description = description, category = cricket, user = user,
	image = "cricket_bgloves.png")
session.add(b_gloves)

description = ("The keeper is the only fielder allowed to touch the ball "
	"with protective equipment, typically large padded gloves with webbing "
	"between the index finger and thumb, but no other webbing. Also, "
	"the webbing shall not protrude beyond the straight line joining the "
	"top of the index finger to the top of the thumb.")
w_gloves = CategoryItem(title = "Wicket Keeping Gloves", 
	description = description, category = cricket, user = user,
	image = "cricket_wgloves.png")
session.add(w_gloves)

description = ("Climbing ropes are typically of kernmantle construction, "
	"consisting of a core (kern) of long twisted fibres and an outer sheath "
	"(mantle) of woven coloured fibres. The core provides about 80% of the "
	"tensile strength, while the sheath is a durable layer that protects the "
	"core and gives the rope desirable handling characteristics.")
ropes = CategoryItem(title = "Climbing Ropes", 
	description = description, category = rock_climbing, user = dummy,
	image = "RC_ropes.png")
session.add(ropes)

description = ("Quickdraws (often referred to as 'draws') are used by "
	"climbers to connect ropes to bolt anchors, or to other traditional "
	"protection, allowing the rope to move through the anchoring system "
	"with minimal friction. A quickdraw consists of two non-locking "
	"carabiners connected together by a short, pre-sewn loop of webbing.")
quickdraws = CategoryItem(title = "Quickdraw", 
	description = description, category = rock_climbing, user = dummy,
	image = "RC_draws.png")
session.add(quickdraws)

description = ("A harness is a system used for connecting the rope to the "
	"climber. There are two loops at the front of the harness where the "
	"climber ties into the rope at the working end using a figure-eight knot. "
	"Most harnesses used in climbing are preconstructed and are worn around "
	"the pelvis and hips, although other types are used occasionally."
	"Different types of climbing warrant particular features for harnesses. "
	"Sport climbers typically use minimalistic harnesses, some with sewn-on "
	"gear loops. ")
harness = CategoryItem(title = "Climbing Harness", 
	description = description, category = rock_climbing, user = dummy,
	image = "RC_harness.png")
session.add(harness)

description = ("Most current players wear specialist football boots, which "
	"can be made either of leather or a synthetic material. Modern boots are "
	"cut slightly below the ankles, as opposed to the high-ankled boots used "
	"in former times, and have studs attached to the soles. Studs may be "
	"either moulded directly to the sole or be detachable, normally by means "
	"of a screw thread.")
shoes = CategoryItem(title = "Shoes", 
	description = description, category = soccer, user = dummy,
	image = "soccer_shoes.png")
session.add(shoes)

description = ("Shin pads must be covered entirely by the stockings, be made "
	"of rubber, plastic or a similar material, and provide a reasonable "
	"degree of protection. The only other restriction on equipment "
	"defined in the Laws of the Game is the requirement that a player must "
	"not use equipment or wear anything that is dangerous to himself or "
	"another player")
pads = CategoryItem(title = "Shin Pads", 
	description = description, category = soccer, user = dummy,
	image = "soccer_pads.png")
session.add(pads)

description = ("There are basically two types of sail materials used in hang "
	"glider sails: Woven Polyester Fabrics, and Composite Laminated Fabrics "
	"made of some combination of polyester film and polyester fibers.")
sailcloth = CategoryItem(title = "Sailcloth", 
	description = description, category = hang_gliding, user = dummy,
	image = "HG_sailcloth.png")
session.add(sailcloth)

description = ("A variometer is a very sensitive vertical speed indicator. "
	"The variometer indicates climb rate or sink rate with audio signals "
	"(beeps) and/or a visual display. These units are generally electronic, "
	"vary in sophistication, and often include an altimeter and an airspeed "
	"indicator.")
variometer = CategoryItem(title = "Variometer", 
	description = description, category = hang_gliding, user = dummy,
	image = "HG_variometer.png")
session.add(variometer)

description = ("Picture shows a collection of differing types of alpine skis, "
	"with nordic and telemark skis at far left. From right: a group of powder "
	"skis, a group of twin-tip skis, a group of carving (parabolic) skis, and "
	"then an older-type non-sidecut alpine ski along with the non-alpine skis."
	)
skis = CategoryItem(title = "Skis", 
	description = description, category = skiing, user = dummy,
	image = "skis.png")
session.add(skis)

description = ("Inline skates are a type of roller skate used for inline "
	"skating. Unlike quad skates, which have two front and two rear wheels, "
	"inline skates typically have two to five wheels arranged in a single "
	"line. Some, especially those for recreation, have a rubber stop or brake "
	"block attached to rear of the frame.")
skates = CategoryItem(title = "Inline Skates", 
	description = description, category = skating, user = dummy,
	image = "roller_skates.png")
session.add(skates)

description = ("A water polo ball is constructed of waterproof material to "
	"allow it to float on the water. The cover is textured to give players "
	"additional grip. The size of the ball is different for men's, women's "
	"and junior games.")
balls = CategoryItem(title = "Balls", 
	description = description, category = water_polo, user = dummy,
	image = "WP_balls.png")
session.add(balls)

description = ("In underwater football, underwater hockey and underwater "
	"rugby, water polo caps are worn by competitors to identify which teams "
	"they are playing for, and to offer some protection to individuals "
	"against the possibility of a burst eardrum caused by the blade of a "
	"fin making direct contact across the ear.")
cap = CategoryItem(title = "Field Player Cap", 
	description = description, category = water_polo, user = dummy,
	image = "WP_cap.png")
session.add(cap)

description = ("A basketball is a spherical inflated ball used in a game of "
	"basketball. Basketballs typically range in size from very small "
	"promotional items only a few inches in diameter to extra large balls "
	"nearly a foot in diameter used in training exercises to increase the "
	"skill of players. The standard size of a basketball in the NBA is 9.5 "
	"to 9.85 inches in diameter.")
ball = CategoryItem(title = "Basketball", 
	description = description, category = basketball, user = user,
	image = "basketball.png")
session.add(ball)

description = ("A basketball sleeve, like the wristband, is an accessory that "
	"basketball players wear. Made out of nylon and spandex, it extends from "
	"the biceps to the wrist. It is sometimes called a shooter sleeve or an "
	"arm sleeve.")
sleeves = CategoryItem(title = "Sleeves", 
	description = description, category = basketball, user = user,
	image = "BB_sleeves.png")
session.add(sleeves)

description = ("The most important factor is the material from which the "
	"racket is made. The qualities of the racket such as flexibility, "
	"weight, sweet spot, etc. depend most on the inner and outer materials "
	"utilized. The outer material of the racquet is usually graphite, Kevlar, "
	"fibreglass and various alloys such as graphite and titanium or Kevlar.")
rackets = CategoryItem(title = "Rackets", 
	description = description, category = beach_tennis, user = user,
	image = "BT_rackets.png")
session.add(rackets)

session.commit()

