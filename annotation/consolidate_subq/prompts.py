consolidation_prompt = \
"""Given questions asked by new or expecting mothers, your task is to identify the assumptions in them. For this task, you will be given a QUESTION asked by a new or expecting mother, some ASSUMPTIONS (as a list of beliefs or assumptions) in those questions identified by health experts, and some possible SUBQUESTIONS (as a list) that public health experts have identified to have the same information goals as the original question. Given all three of these, your task is to consolidate the SUBQUESTIONS and ASSUMPTIONS into a single, exhaustive list, called INFERENCES. Turning a SUBQUESTION into an inference may involve just turning it into a declarative sentence, or identifying the assumptions makde in the SUBQUESTION. Finally, add the INFERENCES to the list of ASSUMPTIONS and remove any duplicates. 

Follow the format given below: 

####
QUESTION: How hard do you have to shake the baby for shaken baby syndrome ?
ASSUMPTIONS: 
Shaking a baby is dangerous.
Some level of shaking is OK
SUBQUESTIONS: 
Is bouncing my baby safe? 
What is a safe and soothing way to move my baby?
How will I know if I am bouncing baby too hard? 
Is any amount of shaking safe? 
What should I do if my baby won't stop crying?
####
INFERENCES: 
There is a condition called shaken baby syndrome.
Bouncing my baby may not be safe.
There exists a safe and soothing way to move my baby.
There is a way to tell if I am bouncing a baby too hard.
Any amount of shaking may not be safe.
####


####
QUESTION: When to stop offering cow's milk to toddler?
ASSUMPTION: 
At some point, toddlers should stop being offered cow's milk. 
Cow's milk should be offered until a certain age. 
SUBQUESTIONS: 
What type of milk should toddlers drink at different ages? 
Is there an age when they should stop drinking milk? 
How much milk should toddlers drink? 
What are benefits/risks of offering cow's milk? 
#####
INFERENCES: 
Toddlers should drink different kinds of milk at different ages. 
There may be an age at which they should stop drinking cow's milk. 
There is a recommended amount of milk that toddlers should drink.
There are some potential benefits of offering cow's milk. 
There are some potential risks of offering cow's milk. 
####

####
QUESTION: How warm of a bath can I take? 
ASSUMPTIONS: 
Baths that are too hot may not be good.
There is a temperature that is OK for baths. 
SUBQUESTIONS:
Is it safe to take a bath while pregnant?
What temperature is safe for a bath in pregnancy? 
What are the risks of taking a bath that is too hot? 
Is the risk the same throughout pregnancy? 
How will I know if the water is too hot without a thermometer? 
####
INFERENCES: 
It is safe to take a bath while pregnant.
There is a particular temperature that is safe for taking a bath while pregnant.
There are risks associated with taking a bath that is too hot. 
There may be different risks associated with warm baths throughout the pregnancy. 
There is a way to know if the water is too hot without a thermometer. 
####

####
QUESTION: How can you tell the difference between postpartum anxiety and exhaustion? 
ASSUMPTIONS: 
There is a recognizable difference between postpartum anxiety and exhaustion. 
It might be hard to tell if someone has anxiety or exhaustion. 
Postpartum anxiety is worse than postpartum exhaustion and it's important to quickly discern the difference.
Postpartum anxiety and exhaustion require different treatments. 
SUBQUESTIONS: 
What are the signs/symptoms of postpartum anxiety? 
What should I do if I think I have postpartum anxiety? 
What are the risks of having untreated postpartum anxiety?
Do I need to contact my doctor if I think I’m experiencing postpartum anxiety?
###
INFERENCES: 
Postpartum anxiety has signs and symptoms.
Postpartum anxiety is different from postpartum exhaustion. 
It might be difficult to tell if someone has postpartum anxiety or exhaustion. 
Postpartum anxiety is worse than postpartum exhaustion. 
Postpartum anxiety might require contacting a doctor for treatment. 
There might be risks to keeping postpartum anxiety untreated. 
####

#### 
QUESTION: How do you know if your baby is draining your breast completely? 
ASSUMPTIONS: 
My baby might not be eating long enough on one side 
My baby might not be getting enough to eat from breastfeeding
SUBQUESTIONS: 
How long should baby feed on one breast before switching?
Why should they nurse fully on one side before changing?
How will I know if my baby is getting enough to eat when nursing?
How long does it take for one breast to "refill" after nursing- ie what is the mechanism if supply/demand for breastfeeding? 
####
INFERENCES: 
There is a reason that babies should nurse fully on one side before changing. 
There is a way to know if a baby is getting enough to eat while nursing. 
There is a mechanism of supply/demand by which breasts 'refill' after nursing. 
There is a way to know if my baby is not nursing long enough at one side. 
My baby might not be getting enough to eat from breastfeeding.
####

#### 
QUESTION: When is it safe to start doing the at home tricks to induce labour?
ASSUMPTIONS: 
There are effective at home tricks to induce labor.
These tricks are safe after a certain point in pregnancy.
These tricks are necessary. 
It is good to speed up onset of labor using at home tricks.
SUBQUESTIONS: 
Do at home tricks to induce labor work? 
What are some things that can be done at home to help induce labor? 
Are at home tricks to induce labor safe?
At what gestational age is it safe for labor to start naturally? 
At what gestational age is a pregnancy considered to have gone on too long and what will your doctor do if they are concerned about a prolonged pregnancy? 
####
INFERENCES:
There are at home tricks that can be done to help induce labor. 
There is a point in pregnancy when it is safe to start doing these at home tricks. 
There is a gestational age at which labor is considered to have gone on for too long. 
There is a potential concern from doctors about a prolonged pregnancy. 
There may be some risks associated with at home tricks to induce labor. 
It may be beneficial to speed up the onset of labor using at home tricks.


####
QUESTION: {question}
ASSUMPTIONS: 
{assumptions}
SUBQUESTIONS:
{subquestions}
####
INFERENCES:

"""