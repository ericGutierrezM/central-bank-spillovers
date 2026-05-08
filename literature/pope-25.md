Discussion Paper
ISSN 2042-2695
No. 2094
April 2025 
Dear brothers 
and sisters: 
Pope's speeches 
and the 
dynamics of 
conflict in Africa
Mathieu Couttenier
Sophie Hatte
Lucile Laugerette
Tommaso Sonno


 
   
Abstract 
Public speeches by leaders can serve as a cost-effective tool for fostering peace, yet their effectiveness remains 
uncertain, particularly in divided societies experiencing violent conflict. This paper examines the impact of the 
Catholic Pope’s peace-promoting speeches on conflict dynamics in Africa. To investigate this, we construct a 
novel dataset covering all papal speeches explicitly addressing violent conflict events in Africa between 1997 and 
2022. Using event-study methods, we find that papal speeches reduce overall conflict by 23% on average. 
However, these effects vary significantly depending on the Pope delivering the speech. While Pope John Paul II 
and Pope Francis’s speeches are associated with substantial reductions in conflict, Pope Benedict XVI’s speeches 
show no significant overall effect but are linked to increased battles and religious violence. We further explore 
four mechanisms driving these heterogeneous effects. First, the impact of papal speeches is significantly stronger 
in areas with a Catholic presence, where violence drops by up to 69%. Second, the effectiveness of a speech 
depends on the bishops’ ideological alignment with the Pope’s vision, with speeches delivered by a Pope who 
appointed the current bishop being 17% more effective. Third, political leaders play a crucial role in amplifying 
the Pope’s message, as violence significantly declines in birth regions of national leaders. Finally, the response of 
armed groups varies depending on their religious affiliation and prior history of violence. 
 
Key words: conflict, violence, religion, leaders, peacebuilding 
JEL codes: D74; F51; Z12 
 
This paper was produced as part of the Centre’s Community Wellbeing Programme. The Centre for Economic 
Performance is financed by the Economic and Social Research Council.  
 
We thank Jean-Pascal Bassino, Simone Bertoli, Matteo Cervellati, Cédric Chambru, Kai Gehring, Gunes Gokmen, 
Etienne Le Rossignol, Nicola Mastrorocco, Elisa Mougin, Hannes Mueller, Alireza Naghavi, Francisco Pino, 
Marta Reynal-Querol, Valeria Rueda, Raphael Soubeyran, Thomas Taylor, Andrea Tesei, Farid Toubal, Mathias 
Thoenig, Ro-main Wacziarg, Ekaterina Zhuravskaya, and participants at seminars at Ecole Normale Supérieure 
de Lyon, University of Paris Dauphine, the CERDI at University Clermont Auvergne, Universitat Autònoma de 
Barcelona, the Facultad de Economía y Negocios at Universidad de Chile, the Centre d’Economie de la Sorbonne, 
the NICEP Seminar at Notting-ham School of Economics, Hertie School and Johns Hopkins, as well as at the 
Workshop on the Economics of Conflict Zones at Paris School of Economics, the Workshop on Political Economy 
of Development and Conflict IX at Barcelona School of Economics, the 3rd Arne Ryde Workshop on Culture, 
Institutions, and Development at Lund University, the CEPR Symposium for useful comments. We thank Alana 
Boone, Tom Buchot, Marion Dury, Lucile Gaultier de Carville, Cassiano Grazini Dos Santos, Kereann Labigand, 
Mateo Moglia, Giacomo Opocher, Pat Patrouille, Shreya Ray, Irene Riz-zoli, Garance Sevestre and Kilourou 
Yénipoho Silué for their excellent research assistance. This work was supported by the French National Research 
Agency of the French Government through the following grant: ANR JCJC grant number ANR-22-CE26-
000.Melanie Arntz, AB Nuremberg and University of Erlangen-Nuremberg.  
Mathieu Couttenier, Ecole Normale Superieure de Lyon; Center for Economic Research on Governance 
Inequality and Conflict and CEPR. Sophie Hatte and Lucile Laugerette, Ecole Normale Superieure de Lyon and 
Center for Economic Research on Governance Inequality and Conflict. Tommaso Sonno, University of Bologna 
and Centre for Economic Performance, London School of Economics. 
 
Published by 
Centre for Economic Performance 
London School of Economic and Political Science  
Houghton Street, London WC2A 2AE  
 
All rights reserved.  No part of this publication may be reproduced, stored in a retrieval system or transmitted in 
any form or by any means without the prior permission in writing of the publisher nor be issued to the public or 
circulated in any form other than that in which it is published. 
 
Requests for permission to reproduce any article or part of the Working Paper should be sent to the editor at the 
above address. 
 
 
 M. Couttenier, S. Hatte, L. Laugerette and T. Sonno, submitted 2025. 


1
Introduction
Conflict remains a critical issue in the contemporary world, directly affecting a substantial propor-
tion of the global population.1 Extensive literature has documented the persistence of violence and
conflict, often rooted in entrenched institutions (Acemoglu et al., 2001), ethnic divisions (McGuirk
and Nunn, 2024; Esteban et al., 2012), and the appropriation of resources (Berman et al., 2017).
However, various local or external factors, such as income disturbances (Dube and Vargas, 2013;
McGuirk and Burke, 2020) and environmental shocks (Miguel et al., 2004; McGuirk and Nunn,
2025), can disrupt the dynamics of violence, either exacerbating tensions and fueling escalation or
creating opportunities for de-escalation and peace. The complex interplay of these factors poses
significant challenges for designing and implementing effective peacebuilding and peacekeeping
policies (Rohner, 2024b).
In this context, public speeches by global leaders emerge as a cost-effective and potentially
powerful tool for fostering peace. Such speeches can simultaneously raise awareness, facilitate di-
alogue, mobilize collective action, and establish normative frameworks conducive to peacebuild-
ing. The capacity of leaders to influence societies, shape institutions, and impact economic growth
has been extensively documented since the seminal works of Jones and Olken (2005, 2009). Pub-
lic information transmitted by influential figures can shift public opinion and reshape behaviours
and norms, as seen in historical examples such as Mustafa Kemal Atatürk, who promoted a new
national identity in modern Turkey (Assouad, 2020), and Philippe Pétain, whose legacy influenced
the diffusion of extreme political behaviours in France’s WWII (Cagé et al., 2023). A more recent
example is President Trump’s impact on social norms and behaviours in the contemporary United
States (Bursztyn et al., 2020; Grosjean et al., 2023; Muller and Schwarz, 2023).2
A key determinant of leaders’ influence is the reach of their message. Substantial evidence
highlights the significant impact of religious leaders (Bassi and Rasul, 2017; Wang, 2021), particu-
larly in Africa, where their authority and extensive networks enable them to engage with diverse
and widespread audiences (Ellis and ter Haar, 1998; Freston, 2001).3 The Catholic Church, with
its unique hierarchical structure and centralized authority in the Pope, has a profound influence.
As the Church’s spiritual, moral, and political leader, the Pope delivers speeches that emphasize
moral and ethical considerations, reinforcing norms against violence and framing peace as both
desirable and achievable. His public addresses focus on reconciliation and forgiveness, addressing
grievances and emotional drivers of conflict while weakening ideological justifications for violence
1In 2024, 12% of the global population was affected by at least one violent political event (battles, explosions, violence
against civilians) and 21% by protests or riots within a 5km radius of their residence (Armed Conflict Location & Event
Data and WorldPop, Conflict Exposure Calculator, downloaded on February 24th, 2025). Predictions are equally striking,
as World Bank estimates show that by 2030, nearly 60% of the world’s extreme poor will live in countries affected by
fragility, conflict, and violence (World Bank, 2024).
2Historical examples further illustrate this potential in times of global tensions, conflict, and war: President John F.
Kennedy’s 1963 “peace race” speech, which contributed to diplomatic progress during the Cold War; Nelson Mandela’s
1998 appeal to end the Northern Ireland conflict; and President Barack Obama’s 2009 address advocating for renewed
relations with the Muslim world. Each underscores the power of international rhetoric in advancing peace agendas.
3In Sub-Saharan Africa, religion plays a central role in daily life, with 85% of individuals (92% of Muslims) consider-
ing it very important, and 75% attending worship services at least once a week. These figures are based on computations
from the Pew Research Center (2010) database, a public opinion survey conducted between December 2008 and April
2009, involving more than 25,000 face-to-face interviews across 19 countries in Sub-Saharan Africa.
2


(Jervis, 1976).
However, the effectiveness of peace-promoting speeches by religious leaders, such as the Catholic
Pope, remains uncertain, especially in divided societies experiencing violent conflict. Such speeches,
rooted in moral and ethical consideration, can reinforce peace norms, reduce mistrust, and encour-
age armed groups to reassess the costs of violence. These messages foster dialogue and mutual
understanding, address commitment problems that hinder peace agreements, and attract interna-
tional attention, further encouraging support for peace initiatives. However, in some cases, armed
groups may perceive these messages as external interference or bias, leading to retaliatory violence.
Additionally, in highly polarized societies, the Pope’s speech may be seen as exacerbating existing
divisions, while structural drivers of conflict, such as competition over resources or territorial con-
trol, could limit the effectiveness of his message.
This paper investigates the effect of the Catholic Pope’s peace-seeking speeches on conflict dy-
namics in Africa. To this end, we construct a unique dataset covering all peace-promoting speeches
delivered by the Pope that explicitly address violent conflict events in Africa over a 26-year period
(1997–2022). A key feature of this empirical setting is its inclusion of various local contexts and
speeches by three different Popes, each bringing distinct ideological orientations and communica-
tion strategies towards Africa.
Transcripts of the Catholic Pope’s speeches are systematically recorded on the Vatican’s official
website for the three pontificates covered by our conflict data: Pope John Paul II, Pope Benedict
XVI, and Pope Francis. While these speeches primarily focus on spirituality, moral values, and
the Catholic Church’s global actions, the Pope also uses them to address conflict zones, highlight-
ing civilian suffering and calling for peace. We identify speeches that explicitly denounce violence
in African countries and call for its cessation, using a combination of statistical topic modeling
and human classification to ensure accuracy. In total, 85 speeches contain peace-promoting mes-
sages targeting at least one conflict in Africa. For identification purposes, we restrict our analysis
to speeches delivered outside the country being referenced, which constitute the vast majority of
cases.4
A crucial assumption underlying the relevance of investigating the effects of the Pope’s speeches
on conflict in Africa is that peace-seeking addresses, often delivered from the Vatican, are effec-
tively disseminated to local audiences. To test this, we first examine media coverage of the Pope’s
speeches in conflict-affected countries in the days following a speech. Using novel data from na-
tional African newspapers, we find a significant increase in the presence of articles mentioning both
the Pope and conflict-related terms in outlets distributed within the country targeted by the speech.
The likelihood of such mentions rises by 5.1 percentage points (34% of a standard deviation) in the
first two days and by 3.6 percentage points (24% of a standard deviation) in the following two
days. We also analyze how papal speeches spread through local Catholic institutions, leveraging
4This restriction excludes speeches directed at countries the Pope is physically visiting. In our sample, 88.3% of
speeches were delivered from the Vatican, while 11.7% were given during official visits to foreign countries but ad-
dressed issues in nations other than the host country. This restriction is motivated by the fact that papal visits are
planned years in advance, and the Pope’s physical presence in a country significantly influences key outcomes in our
empirical context, such as heightened security measures. As a result, disentangling the effects of a speech from the
broader impact of the Pope’s visit becomes challenging.
3


original data on the Facebook activity of dioceses. The likelihood of a diocese posting about a
speech increases significantly after a two-day lag, peaking at 6.7 percentage points (29% of a stan-
dard deviation) on days three and four before returning to baseline. The short-lived nature of these
effects, along with the absence of pre-trends, supports the interpretation that the increase in cover-
age reflects the diffusion of papal speeches across both national media and the Facebook pages of
local dioceses. Interestingly, the lag in diocesan communication likely reflects the time needed to
process and disseminate the messages, in contrast to professional media, which can publish imme-
diately. Finally, using Afrobarometer survey data, we find that Christian respondents interviewed
after a papal speech mentioning their country and conflict report a higher perceived importance
of religion and greater trust in religious leaders, with no significant effects observed among non-
Christian respondents.
The central focus of this paper is to estimate the impact of a papal speech directed at an African
country on conflict incidence in the following weeks. The analysis is conducted at the level of a
week-by-cell grid, where each cell measures 0.5×0.5 degrees in latitude and longitude (approxi-
mately 55 km × 55 km at the equator). The sample includes weeks surrounding a speech specif-
ically addressing the country corresponding to each cell. For the empirical strategy, we use an
event-study approach, defining the event as a week (or a series of weeks, if the Pope gives multiple
peace-seeking speeches targeting the same conflict within a short period of time) during which a
papal speech is directed at a given African country. We then compare the incidence of conflict be-
fore and after the speech within the affected country, using a window extending from five weeks
prior to eight weeks following the speech. Since the Pope occasionally addresses multiple conflicts
in a single speech, our dataset of 85 speeches translates into 100 isolated “speech events.”5 Conflict
incidence is measured using the Armed Conflict Location and Event Dataset (ACLED), which pro-
vides detailed information on conflict events, including the date, location, involved armed groups,
and event type. However, ACLED does not indicate whether religion plays a role as a motivating
factor in these conflicts. An empirical contribution of this paper is the use of a prompt-based clas-
sification approach, leveraging a pre-trained large language model (via OpenAI’s API) to analyze
event descriptions for a large subset of events and identify whether an event is religious in nature—
such as when religious beliefs, affiliations, or leadership are central. This method is also used to
assess whether armed groups can be identified as having a religious affiliation.
The baseline estimates highlight the significant impact of the Pope’s speeches on conflict dy-
namics. Overall, papal speeches are associated with a 23% reduction in conflict incidence. This
effect varies by type of violence, with a 27% reduction in battles and a more pronounced 34% de-
crease in low-intensity events. Speeches by John Paul II and Francis significantly reduce conflict,
with overall decreases of 89.5% and 21%, respectively. John Paul II’s impact is concentrated in bat-
tles, while Francis’ speeches show broader effects, reducing battles and low-intensity events. In
contrast, speeches by Benedict XVI show no significant overall effect on conflict but are associated
with substantial increases in battles (85.8%) and religious events (60%). This suggests potential
unintended escalations, possibly influenced by the timing, content, or reception of his speeches,
5See Section 3.2 for details on the definition of a speech event.
4


or broader policies during his tenure. We identify a specific turning point–the 2006 Regensburg
speech–after which Benedict XVI’s speeches start to be associated with an increase in conflict.
While this speech likely shaped the reception and effects of his messages, other factors, including
broader policies during his tenure, may also play a role. In a similar exercise, we assess whether
UN Security Council resolutions, as a formal peacekeeping institution, achieve outcomes similar
to the Pope’s speeches. While the likelihood of African newspapers articles mentioning the UN Se-
curity Council rises after the resolution, we find no impact on conflict dynamics. This suggests
that religious institutions influence conflict differently, with papal speeches shaping behaviour
through moral authority rather than enforcement mechanisms (Iannaccone, 1998; McCleary and
Barro, 2006).
Finally, in the last part of our analysis, we examine four key mechanisms. First, building on the
idea that audience identity shapes a message’s impact (DellaVigna et al., 2014), we assess whether
the Pope’s speeches have similar effects on conflict in areas with and without Christian communi-
ties. As expected, we find that violence significantly decreases in areas with Christian communities
following a speech, with an overall reduction of 33.5%, a 48% drop in low-intensity events, and a
69% decline in religious violence. In contrast, no discernible effect is observed in regions with-
out Christian communities. Second, we explore the role of local religious institutions—specifically
Catholic bishops—in amplifying the Pope’s message. We find that the speeches’ effectiveness de-
pends on the bishop’s ideological alignment with the Pope: the pacifying effect increases by 17% in
places where the current bishop was appointed by the Pope delivering the message, compared
to those where the bishop was appointed by a previous Pope. Additionally, while a bishop’s
local experience (years in the diocese before the speech) has little measurable effect, overall ex-
perience (years since ordination) significantly enhances the speeches’ impact, particularly in re-
ducing low-intensity and religious violence. Third, we examine whether the Pope’s speeches, by
drawing global attention to a country, influence political leaders to act in ways that reduce vio-
lence—particularly in their stronghold regions. We find that violence decreases significantly in
a leader’s birthplace region after a speech, with a 71% drop in low-intensity events (compared to
45% elsewhere) and an 87% decline in religious violence (compared to 67%). These results highlight
the interaction between the Pope’s message and national leadership in shaping conflict dynamics.
Fourth, we analyze how armed groups respond to the speeches, focusing on their religious affilia-
tion and prior history of violence. Using bilateral links between actors in the same event window
and country, we find that violence decreases by 45% overall for actor pairs with no religious affili-
ation, by 60% for pairs with at least one Christian group, and shows no significant effect for pairs
with at least one Islamic group. Specifically for religious violence, conflict declines by 70% for pairs
with at least one Christian group but increases by 230% for pairs with at least one Islamic group,
underscoring the varied impact of the Pope’s message based on religious affiliation. Additionally,
the speeches reduce overall violence and battles by 210% when groups have no prior conflict. How-
ever, for groups with a long-standing history of violence (more than 10 events since 1997), conflict
likelihood increases by 30% across overall violence, battles, and religious violence. This suggests
that while the speeches help de-escalate less entrenched conflicts, they may escalate hostilities or
5


prompt strategic reactions in deeply rooted conflicts.
Contribution to the literature.
This paper contributes to several strands of the literature. First, it
adds on the determinants of conflict where factors such as ethnic diversity (e.g., Cederman et al.,
2009), weather conditions (e.g., Harari and Ferrara, 2018; Eberle et al., 2020; McGuirk and Nunn,
2025), natural resources (e.g., Dube and Vargas, 2013; Berman et al., 2017), agriculture productivity
(e.g., McGuirk and Nunn, 2024; Iyigun et al., 2017; Cervellati et al., 2022; Berman et al., 2021), and
cultural distance (Guarnieri and Tur-Prats, 2023; Guarnieri, 2025) have been of particular interest.
Specifically, it contributes to the literature examining the extent to which external shocks–those
outside the conflict zone, such as fluctuations in global prices–affect conflict dynamics (Dube and
Vargas, 2013; Berman and Couttenier, 2015; McGuirk and Burke, 2020, 2022). Our paper also aligns
with the call made in Rohner (2024a) on the challenges of conflict interventions aimed at resolu-
tion through mediation, military peacekeeping operations, and financial support. It emphasizes
the need for more robust statistical analyses and cross-country studies on third-party interventions
through mediation. We contribute to understanding the role of peacekeeping interventions in mit-
igating violence, demonstrating that external actors, in our case a major religious leader, can foster
stability through both mediation and enforcement mechanisms (Rohner and Zhuravskaya, 2023;
Rohner, 2024b).6
Second, while the economics of religion literature has flourished in recent years, few studies
explore the interplay between religion and conflict, particularly in Africa.7 This gap arises partly
from the difficulty of measuring religiously motivated violence and distinguishing it from other
factors, such as ethnicity. One notable exception is Anderson et al. (2025), who use a dictionary-
based method to show that a quarter of violent events in Africa are linked to religion. We con-
tribute to this emerging literature by introducing a novel methodology to identify religious conflict
events using a prompt-based machine learning approach (via OpenAI’s API). We leverage this data
to demonstrate how violence overall, and religious violence in particular, are influenced by peace-
seeking messages from a leading religious authority. In line with this approach, Laville (2021) show
in a cross-country analysis that the travels of John Paul II reduced the risk of conflict in host coun-
tries. We extend the analysis by focusing on papal speeches delivered from outside the conflict zone
(often from the Vatican), which allow for stronger causal identification and are more frequent and
less costly than papal visits to Africa. By examining variation in responses across different papacies
and local contexts, we show that these remote speeches can de-escalate violence. However, we also
reveal significant heterogeneity in this effect, driven by the Pope’s identity and characteristics of
the local conflict zone, including local religious institutions and armed groups. Our finding that
local religious institutions are key drivers of the effects complements Martinez-Bravo et al. (2025),
6See Rohner (2024a) for a comprehensive review of the extensive literature on third-party interventions, spanning
both economics and political science.
7Religious institutions function as both social and economic entities, influencing political stability and collective
action (Iannaccone, 1998; McCleary and Barro, 2006). Recently, religion has been shown to impact economic growth
(Becker et al., 2024), social behaviour (Bassi and Rasul, 2017), and political outcomes (Wang, 2021; Bentzen and Gokmen,
2023; Bentzen et al., 2025). Engelberg et al. (2016) examine the supply side of religion, showing that the quality of
religious leaders significantly impacts congregation growth and engagement. For a comprehensive literature review, see
Iyer (2016).
6


who show that the appointment of bishops under John Paul II’s papacy influenced redistributive
conflict in Brazil, where landless peasants invaded large estates to demand land redistribution.
Our paper contributes also to the growing literature on how media can both exacerbate and al-
leviate violence. Media can facilitate insurgent coordination and fuel violence (Gagliarducci et al.,
2020; Adena et al., 2015; Yanagizawa-Drott, 2014) but counter-narratives, such as broadcasts pro-
moting defection, can reduce violence and support long-term reconciliation (Armand et al., 2020;
Esposito et al., 2023). Ethnic divisions often shape how media impacts conflict, with partisan narra-
tives strengthening group identities and intensifying tensions (Glaeser and Sunstein, 2009; DellaV-
igna et al., 2014; Mougin, 2024). However, media can also help reduce polarization and tensions
by addressing informational asymmetries (Allport, 1954). Our contribution is in documenting that
the dissemination of a religious peace message, particularly through media, can help reduce the
intensity of violence, even in conflicts where religious identity plays a significant role.
Finally, we also contribute to the literature on leadership. Previous work has emphasized the
role of political leaders in shaping economic outcomes (Bertrand and Schoar, 2003; Jones and Olken,
2005), with a particular focus on the connection between leaders and their birth regions (Hodler
and Raschky, 2014; Burgess et al., 2015). Many evidence illustrate how leaders have shaped na-
tional identity, ideology, and social behaviours through their rhetoric (Assouad, 2020; Bursztyn
et al., 2020; Cagé et al., 2023; Grosjean et al., 2023; Muller and Schwarz, 2023). Our results high-
light that, in certain contexts, religious discourse enhances the effectiveness of peace-promoting
efforts by simultaneously raising awareness, facilitating dialogue, mobilizing collective action, and
establishing normative frameworks conducive to peacebuilding.
2
Pope’s peace-targeting speeches and violent conflicts
In the following, we explore the theoretical reasons behind the ambiguous effects of the Pope’s
speech on violence dynamics. We also analyze how factors such as the Pope’s identity, local reli-
gious institutions and the characteristics of armed groups influence variations in violence responses
to his speeches.
2.1
Conceptual framework
Speeches promoting peace by influential leaders—including the Catholic Pope—have an ambigu-
ous impact on violent conflicts. On one hand, they can catalyze peace by addressing key drivers
of conflict, as outlined in Blattman (2022).8 First, papal speeches target unchecked interests that
perpetuate wars (Acemoglu et al., 2001). By invoking moral and ethical considerations, they re-
inforce peace norms and promote reconciliation. These speeches may prompt armed groups to
reassess the costs and benefits of violence, particularly in regions where the Pope holds signifi-
cant influence and among groups with religious affiliations. Second, the Pope’s focus on shared
values and inter-religious dialogue help reduce mistrust and uncertainty among armed groups
8In his recent book, Blattman (2022) argues that violence is primarily driven by unchecked leadership, uncertainty,
commitment problems, intangible incentives, and misperceptions.
7


(Fearon, 1995; Sawyer, 2004), fostering mutual understanding and creating a foundation for recon-
ciliation. Additionally, the Pope can act as a mediator, addressing commitment problems (Walter,
1997; Fearon and Laitin, 2004) by strengthening armed groups’ trust in the viability of negotiated
solutions. Third, the Pope’s ability to draw international attention encourages external actors in
support of peace initiatives, facilitating agreements, humanitarian aid, and peacekeeping efforts,
thereby reducing incentives for violence (Petersen, 2002).
On the other hand, papal speeches addressing conflicts, though intended to promote peace,
can paradoxically escalate violence. A key factor is the perception of the message among target
populations (Galtung, 1969; Autesserre, 2014). Armed groups may interpret the Pope’s message as
external provocation, favoritism toward adversaries, or an attack on their legitimacy (Tilly, 2003;
Powell, 2006), prompting them to escalate violence as a show of strength or resistance to perceived
interference. Victims of violence or marginalized groups might perceive the speech as biased or
unjust, fueling resentment and retaliation. Armed groups may also reinterpret the message to jus-
tify violence (Wood, 2003; Kalyvas, 2006), framing it as a defense of peace or stability. Furthermore,
in polarized contexts—characterized by ethnic, religious, or ideological divides—the speech may
deepen tensions by being interpreted in ways that exacerbate existing divisions (Cederman et al.,
2011). Another factor relates to heightened expectations. Peace-promoting speeches often raise
hopes among populations and combatants, and when these expectations remain unfulfilled, frus-
tration can amplify grievances and incite violence (Pruitt and Kim, 2004; Pearlman, 2013). Finally,
opportunistic reactions may occur. Temporary reductions in violence or shifts in priorities follow-
ing the Pope’s speech could create opportunities for rival groups to escalate localized violence or
strategically reallocate resources (Weinstein, 2007; Walter, 2014).
The Pope’s message may also have a neutral effect on violence. Armed groups may not ac-
knowledge his moral authority or may perceive his speeches as irrelevant to their immediate con-
cerns. Furthermore, structural and strategic factors, such as territorial control or competition for
resources (minerals, fertile land, water), often drive conflict dynamics, leaving little room for mes-
sages grounded in ethical principles and moral appeals. Finally, limited dissemination in remote or
isolated regions could prevent the message from reaching key actors, further reducing its influence.
2.2
Identity of the Catholic Pope
Research in social and political psychology highlights that the perceived credibility, legitimacy, and
affiliations of a speaker strongly influence how audiences interpret and respond to their messages
(Seyranian and Bligh, 2008; Seyranian, 2014). A leader’s identity can even enhance the resonance
of their message to some groups while simultaneously alienating or provoking opposition from
others. Across different papacies, the Pope’s personal background, theological priorities, and com-
munication style may either facilitate or limit the effectiveness of a message. Our empirical setting
spans 26 years (1997–2022) and three distinct Catholic leaders, providing a unique opportunity to
study how variations in papal identity shape the reception and impact of peace-seeking speeches.
John Paul II, Benedict XVI, and Francis each adopted markedly different approaches, particularly
in their engagement with and communication about Africa.
8


Pope John Paul II (October 16, 1978, to April 2, 2005) was a highly influential figure, known for
his strong advocacy of human rights and inter-state peace.9 He viewed the Church as a universal
institution advocating for reconciliation and dialogue (John Paul II, 1995). His critical role in end-
ing the Cold War, his appeals for peace during the Gulf War, and his continued advocacy for global
nuclear disarmament exemplify this priority.10 He placed Africa at the center of his global geopo-
litical agenda, emphasizing its challenges and potential through a series of influential speeches and
initiatives (John Paul II, 1994). His advocacy for economic justice, including debt relief (e.g., 1987
UN address), and the promotion of human dignity as foundational to peace (1995 Evangelium Vi-
tae), reinforced the need to view Africa as a partner rather than a mere aid recipient (1994 Ecclesia
in Africa).11 His 14 visits to 42 African countries (some of them multiple times), over a third of his
total travels, underscored this commitment. By advocating a shift from aid to trade and positioning
bishops as key societal actors, he established the Church as a pivotal force in political and social
transitions.
Pope Benedict XVI (April 19, 2005, to February 28, 2013), unlike his predecessor, made few vis-
its to Africa, traveling to only three countries (13% of his total travels). His papacy, characterized
by theological conservatism (Thornton and Varenne, 2008), prioritized traditional Church values,
doctrinal clarity, and Western principles (Seewald, 2020; Rowland, 2008; Marshall, 2012). This doc-
trinal emphasis posed challenges in Africa, where interfaith dynamics and cultural sensitivities
required a more pastoral and inclusive approach. Benedict XVI’s Regensburg speech in 2006 be-
came controversial due to a quotation perceived as critical of Islam, sparking protests and straining
interfaith relations.12 His opposition to condom use to combat AIDS during his visit to Cameroon
further illustrates the challenges arising from his doctrinal approach in Africa. This stance gener-
ated controversy, raising critical questions about the Church’s role in public health and highlighting
tensions between theological principles and the urgency of pragmatic health interventions.
Pope Francis (since March 13, 2013) has prioritized decentralization and dialogue, emphasizing
the empowerment of local Churches to foster inclusivity and diversity (O’Connell, 2019). His pas-
toral approach and focus on social justice have defined his papacy, with his four visits to Africa
9His unwavering stance on these issues contributed to his canonization, making him one of only three popes of the
20th century to have been declared a saint.
10John Paul II supported the Solidarity movement in Poland (e.g., his speeches during the 1979 visit to Warsaw empha-
sized human dignity and freedom), inspiring systemic change. His efforts included diplomatic advocacy, collaborating
with global leaders like Ronald Reagan and Margaret Thatcher to dismantle oppressive regimes (Weigel, 1999). In his
1981 Encyclical, Laborem Exercens, he highlighted the dignity of labor and the rights of workers, indirectly challenging
communist practices. During the Gulf War, he repeatedly appealed for peace (e.g., his public statement in 1991 and his
letters to U.S. President George H. W. Bush and Iraqi leadership calling for an end of hostilities) and persistently called
for global nuclear disarmament.
11In Ecclesia in Africa (1994), John Paul II emphasizes the pastoral role of bishops in promoting justice, peace, and
development across African nations. It highlights the Church’s responsibility in addressing socio-political challenges
and underscores the importance of collaboration among Church leaders and local communities to foster reconciliation
and societal transformation.
12In his speech, Pope Benedict XVI cited a dialogue between the 14th-century Byzantine emperor Manuel II Palaiolo-
gos and a Persian scholar, where the emperor stated that spreading faith through violence is unreasonable and contrary
to the nature of God. Although Benedict XVI did not explicitly endorse the statement, its inclusion was widely inter-
preted as a critique of Islam, leading to significant backlash in many Muslim-majority countries. Ayman al-Zawahiri,
the second-in-command of Al-Qaeda, declared in a video message released on an Islamist website on September 29,
2006, that “this charlatan accused Islam of being incompatible with reason, while forgetting that his own Christianity is
unacceptable to any rational mind” (L’Orient Le Jour article from September 30, 2006).
9


reflecting a commitment to addressing social inequalities and advocating for marginalized com-
munities. His engagement with independent Churches and interfaith initiatives, particularly in
Sierra Leone, underscores his efforts to foster dialogue beyond Catholic communities, reinforcing
the Church’s role in peace and reconciliation. This approach aligns with “Evangelii Gaudium,”
where he emphasizes dialogue as a means of promoting mutual understanding and societal heal-
ing (Francis, 2013).
2.3
Local religious institutions and the transmission of peace messages
Beyond the identity of the Pope, local religious institutions play a pivotal role in shaping the trans-
mission and reception of peace-seeking messages. Embedded in their social, cultural, and political
contexts, these institutions act as intermediaries, translating global appeals into locally relevant
contexts. Their effectiveness depends on alignment of local leaders with the Pope’s message, the
institutional capacity to mobilize communities, and the broader sociopolitical environment.
Historically, African bishops have played a pivotal role in justice, peace, and reconciliation
(Hastings, 1994).13 Under John Paul II, the Post-Synodal Apostolic Exhortation Ecclesia in Africa
(1994) reinforced their leadership in societal transitions, exemplified by mediation efforts dur-
ing civil conflicts in Sudan (Hutchinson, 1996) and Rwanda (Prunier, 1997).
During Benedict
XVI’s papacy, the Post-Synodal Apostolic Exhortation Africae Munus (2011) reaffirmed bishops’
role in peace and reconciliation, though tensions arose between doctrinal priorities and pragmatic
needs.14 Under Francis, bishops have prioritized grassroots engagement and interfaith collabora-
tion. Guided by “Evangelii Gaudium”, they have focused on local communities and key socio-
political issues such as migration, poverty, and climate change. Notably, bishops in the Democratic
Republic of Congo (Turner, 2007) and South Sudan (Johnson, 2011) have played critical roles in
mediating peace and supporting conflict resolution, reflecting Francis’s vision of a Church closely
connected to its people.
Two key factors shape their effectiveness. First, alignment with the Pope’s vision ensures coher-
ence in addressing challenges but can create tensions when bishops were appointed by a predeces-
sor with different priorities.15 For instance, bishops appointed by Benedict XVI, often characterized
by theological conservatism, have at times faced challenges in aligning with Pope Francis’s more
decentralized and inclusive approach.16 Second, extensive pastoral experience—gained through
13Throughout the 20th and 21st centuries, they have been important in promoting justice, peace, and reconciliation
during periods of significant turmoil (Orobator, 2018). Guided by papal directives and their pastoral missions, bishops
have often assumed responsibilities beyond traditional religious duties, advocating for systemic change and societal
reconstruction.
14For example, see articles in The New York Times (2009), “Pope’s Comments on Condoms Set Off International
Criticism,” and BBC News (2006), “Pope’s Speech Stirs Muslim Anger.”
15The appointment of bishops follows a hierarchical process: local bishops propose candidates, the apostolic nuncio
gathers confidential assessments, and the Holy See reviews a shortlist before the Pope makes the final decision. Episcopal
consecration is required before assuming office, with papal approval remaining essential across rites (John Paul II, 1983).
See Online Appendix H for additional details on this procedure.
16Ivereigh (2014) discusses resistance from bishops appointed during Benedict XVI’s papacy, notably during the Synod
on the Family (2014–2015) and in opposing Francis’s financial transparency and decentralization efforts. These tensions
have been covered by The Guardian (2017) and National Catholic Reporter (2023), while Lamb (2020) provides an in-
depth analysis of the broader challenges faced by Pope Francis in his reform efforts.
10


decades of service as priests before assuming episcopal roles—equips bishops with knowledge of
local cultures and community challenges, fostering the trust and credibility essential for mediation
in complex contexts (Orobator, 2018). However, long tenures can also result in entrenched per-
spectives and resistance to change, limiting adaptability in rapidly evolving environments. This
aligns with Blattman (2022), who argues that institutional rigidity and fixed positions can hinder
flexibility and innovative conflict resolution.
2.4
Local political leaders
National political leaders shape the local impact of papal messages, which, through media cover-
age, can either amplify peace-oriented messages or deepen divisions if perceived as biased (Tarrow,
2005; Blattman and Miguel, 2010). In many African countries, leaders’ influence is concentrated in
their home regions, where they prioritize infrastructure and policy implementation (Franck and
Rainer, 2012; Hodler and Raschky, 2014; Burgess et al., 2015). While strong ties to their birthplace
can facilitate resource mobilization and alignment with papal messages, they may also reinforce
regional inequalities, limiting the broader reach of papal appeals and conflict resolution efforts.17
3
Data and Empirical Strategy
3.1
Data
Unit of Analysis.
To analyze conflict dynamics, we use 0.5 × 0.5 degree grid cells (≈55 × 55km)
across Africa, maintaining this structure for the weeks surrounding the Pope’s speeches from 1997
to 2022. This approach helps mitigate the potential endogeneity of political boundaries.18
Conflict data.
We use the Armed Conflict Location and Event Dataset (ACLED, Raleigh et al.
2010) which covers conflict events in African countries from 1997 to 2022.19 ACLED reports infor-
mation about the date, location, type of violence, and actors for each event. Events are compiled
from various sources, including press accounts from regional and local news, humanitarian agen-
cies, and research publications. The dataset contains information on 325,541 distinct violent events.
Following the strategy developed in Couttenier et al. (2024), we keep only events with the highest
level of geographical precision, i.e. town level (events coded as “part of a region”, “region”, or
“country” are excluded) leaving us with 240,334 events. ACLED reports information on the nature
17Political leaders’ alignment with the Church varies—some may leverage papal messages to enhance legitimacy or
unity, while others may resist due to ideological differences. For instance, Nelson Mandela embraced the Pope’s calls
for reconciliation in 1995, supporting South Africa’s post-apartheid healing. Conversely, Augusto Pinochet sought to
co-opt the Pope’s 1987 speeches to legitimize his regime, though the Pope’s criticisms resonated more with opposition
leaders. Our analysis, however, focuses on the sub-national level, examining leaders’ regions of origin to provide a more
granular understanding of these dynamics.
18See Harari and Ferrara (2018); Berman et al. (2017); McGuirk and Nunn (2025); Eberle et al. (2020) for papers using
similar spatial unit of analysis.
19Downloaded on June 28th, 2023. See Michalopoulos and Papaioannou (2016); Berman et al. (2017); Harari and
Ferrara (2018); Eberle et al. (2020) for papers using ACLED data.
11


of violence associated with each event (battles, explosions/remote violence, protests, riots, strate-
gic developments, and violence against civilians), but it provides no information on whether the
event may be motivated or explained by religious reasons. We propose a strategy to overcome this
limitation by leveraging a unique feature of ACLED, which provides a description of the event
for a large subset of the events and using a prompt-based classification approach (via OpenAI’s
API). An event is classified as religious if religious beliefs, affiliations, or leadership play a central
role. This approach is also applied to armed groups to determine whether we identify them with
a religious affiliation, such as Christian or Islamic. Accordingly, we define an event as a religious
event if a group is identified as religious or if the text classification model indicates that the event is
religious.20 See Online Appendix A for examples, the prompt used and some relevant statistics.
Pope’s speeches.
For each of the three pontificates overlapping the ACLED time period (Pope
Francis, Pope Benedict XVI, and Pope John Paul II), the transcript of each speech has been recorded
and made freely available on the Vatican’s official website.21 These documents include all official
addresses of the Catholic Pope, varying in subject matter and length.22 The majority of papal
speeches are delivered from the Vatican, with only 5% given during papal travels. As discussed
further in Section 3.2, we exclude all speeches targeting countries that the Pope is physically visiting
for identification purposes.
Between 1997 and 2022, 1’438 unique documents mention at least one African country. Since
our aim is to detect peace-seeking speeches, a key challenge is identifying explicit references to
conflict events. To ensure the accurate identification of speeches mentioning conflicts in Africa,
and minimize both false positives and false negatives, we follow a two-step strategy. First, we
use statistical topic modelling to exclude irrelevant speeches. Specifically, we apply the Correla-
tion Explanation (CorEx) model, a learning approach used in the literature to detect political and
conflict-related news (Hatte et al., 2021; Djourelova et al., 2024). The model takes preprocessed text
as input and outputs two key elements: the top words associated with each topic and the proba-
bility distribution of topics across documents. The number of topics to be detected is set to 25, and
we do not anchor any topic, as the outcomes of this unsupervised CorEx method naturally yield
relevant topics. Table B1 in Online Appendix B presents the list of topics. As expected, the five
most prevalent topics in papal speeches relate to the Catholic Church, spirituality, and moral val-
ues.23 We focus on the conflict topic detected by the model (Figure B2 in Online Appendix B, which
presents the word cloud of this topic) and exclude all speeches where the probability of the conflict
topic is below 10%. Second, we manually verify those that mention an African country, resulting in
386 distinct speeches. Each speech was labelled by two human annotators, with discrepancies re-
20To our knowledge, two teams have started to collect information on religious conflicts. First, ACLED has under-
taken a pilot project to collect data on religious repression and unrest (ACLED-Religion). This pilot focuses on seven
countries—Bahrain, Egypt, Iran, Iraq, Israel, Palestine, and Yemen—over the period from January 2020 to March 2022.
Second, Anderson et al. (2025) use a dictionary-based method to classify events as religious based on the event descrip-
tions in ACLED.
21https://www.vatican.va
22The length of the speeches is highly heterogeneous, ranging from 200 to 17’000 words, with an average of 3’250.
23These five topics are “spiritual journey” (present with a probability greater than 0.5 in 53% of speeches), “journey,
memory, and hope” (40%), “values” (37%), “inner struggles” (37%), and “truth, meaning, and fulfillment” (33%).
12


solved by a third reviewer. Ultimately, 85 speeches were identified as explicitly addressing conflict
in Africa. Since some of these documents reference multiple conflict zones in Africa, this results in
a total of 131 individual peace-seeking messages delivered by the Catholic Pope in response to con-
flicts in Africa.24 Online Appendix B provides further details on the data, while Online Appendix
C discusses the data generating process of the Pope’s speeches.25
Bishops.
We use the Catholic Hierarchy website, which provides detailed information on the
structure of the Catholic Church, including current and historical data on bishops and dioceses.26
From this source, we compile historical data on 1’810 bishops, including their appointment dates,
birth details, and career trajectories, specifying the dioceses where they served as priests and bish-
ops.27 The richness of the data allows us to define three specific characteristics for bishops. First,
the Pope who appointed them. Second, a general measure of experience based on the number of
years since their ordination as a priest (overall experience). Finally, a measure of experience accu-
mulated within their diocese, approximated by the number of years between their arrival in the
diocese and the date of the Pope’s speech (local experience). In our sample, bishops are on average
62 years old, with 35 years of overall experience and 12 years of local experience in the diocese. The
boundaries of African dioceses were retrieved from the Catholic Geo Hub.28
Google Maps.
To approximate the diversity of religious presence within cells, we collected ge-
olocation data on places of worship from multiple denominations, including their type and name,
using Google Maps.29 In total, 332’794 distinct places of worship were scrapped, and within our
final sample of 7’319 cells, 2’002 contain at least one Christian place of worship.
Additional data: African newspapers, Facebook posts of African dioceses, Afrobarometer, UN
security council resolutions, and identity of national leaders.
We exploit five additional datasets.
First, to document the coverage of papal speeches in African national news, we gathered novel data
on all stories published in national newspapers included in Factiva and Europresse around the
time of speeches targeting a given country. This data collection resulted in articles from 27 national
newspapers across 13 African countries. Specifically, we track the presence of articles mentioning
24The average likelihood of the conflict topic appearing in the final sample of speeches is 74%.
25In Online Appendix C, we examine speeches timing and content to characterize the factors driving Pope’s interven-
tions. Low levels of democratization, major events such as natural disasters or terroristic attacks, and conflict situations
predict papal addresses to specific countries. However, when focusing on within-country variation in the likelihood
of being mentioned by the Pope, we show that the key determinant–particularly for peace-promoting speeches–is the
ongoing and prolonged presence of violence.
26https://www.catholic-hierarchy.org/
27In our sample, 281 bishops have been appointed by Paul VI ; 474 by John Paul II ; 196 by Benedict XVI and 214 by
Francis.
28Downloaded on 4th, July 2023. Stored on ArcGIS REST Servers. Global Diocesan Boundaries: Burhans et al. (2016).
See Online Appendix E to visualize the African dioceses.
29Churches, Mosques, Temples and Synagogues. Data accessed in October 2024. Data on churches was cross-checked
with the Annuario Pontifico at the diocese level; however, official Vatican data appears to underestimate the number of
churches as some locations listed on Google Maps may be unofficial buildings or open-air worship sites. Additionally,
the higher precision of Google Maps data allows us to estimate religiosity at the cell level for multiple denominations,
which would not be feasible using official Vatican sources.
13


the Pope alongside at least one element of conflict-related lexicon.30 Second, we collected original
data on the diffusion of papal speeches on the Facebook pages of African dioceses around the time
of speeches targeting a given country. To achieve this, we first manually identified whether each
diocese in Africa had an official Facebook Page. We then scraped all posts published on these pages
using Meta’s CrowdTangle platform and identified mentions of the Pope as well as the presence
of the conflict-related lexicon used in the newspaper data analysis. This process resulted in a post-
level database covering 151 dioceses in 35 African countries from 2010 to 2022. As Facebook usage
in Africa has expanded significantly in recent years–particularly since 2015 (Hatte et al., 2025)–the
vast majority of the posts (89%) in our dataset come from the 2015–2022 period. Third, we incor-
porate data from three rounds of the Afrobarometer survey, focusing on attitudes toward religion.
Specifically, we examine respondents’ views on the importance of religion in their daily lives, their
trust in religious leaders, their tolerance toward neighbors of different religions, and their perceived
discrimination based on religion. Fourth, we collect from the UN Security council webpage 1553
distinct resolutions from 1997 to 2022. Fifth, we collected additional information on the religious
affiliation and place of birth of all African national leaders from 1997 to 2022. See Online Appendix
C.1 for more details.
3.2
Empirical strategy
We aim to document the effect of peace-seeking speeches delivered by the Catholic Pope on the
dynamics of violence in Africa.
Event-study estimation.
We estimate the following equation:
Con f lictk,i,s,t = βPosti,s,t + ηk + ωt + µi,s + ϵk,i,s,t
(1)
Where Con f lictk,i,s,t represents the incidence of conflict in cell k, in country i, during week t,
within an event window spanning from 5 weeks before to 8 weeks after the Pope’s speech s. The
variable Posti,s,t is a binary indicator equal to 1 for weeks following a Pope’s speech mention-
ing country i, and 0 otherwise. Crucially, we include three sets of fixed effects to address key
challenges in the estimation. First, we include cell fixed effects (ηk) to control for time-invariant
cell-specific characteristics, such as geographic or historical factors. Second, we incorporate week-
of-the-year fixed effects (ωt). These fixed effects account for time-specific shocks unrelated to the
Pope’s speeches but affecting all cells simultaneously. Examples include recurring seasonal fac-
tors (e.g., reduced activity during major holidays such as Christmas or Easter), global or regional
conflict dynamics, or systematic variations in social, economic, or political conditions associated
with specific weeks of the year. By absorbing these time-varying influences, week-of-the-year fixed
effects isolate variation in conflict levels that can plausibly be attributed to the speeches, ensuring
30The conflict lexicon includes the following keywords: conflict, peace, war, peacebuilding, mediation, negotiation,
resolution, reconciliation, ceasefire, diplomacy, violence, hostility, humanitarian, disarmament, truce, tension, crisis,
victim, death, suffering, loss, grief, insecurity, justice, hope, trauma, and injury. Keyword searches were conducted in
the languages of the newspapers: Arabic, English, French, Portuguese, and Spanish.
14


the estimates are not confounded by broader temporal fluctuations in violence. Third, we include
event-window-by-country fixed effects (µi,s), which capture time-varying dynamics specific to a
country during the event window. These dynamics may include shifts in government policy, esca-
lation or de-escalation of conflict at the country-level, or heightened international attention to the
region, which could simultaneously influence both conflict levels and the likelihood of a Pope’s
speech. Robust standard errors are clustered at the cell level.
We acknowledge that the Catholic Pope delivers peace-seeking messages targeting places ex-
periencing conflict (mechanically), which makes comparing conflict dynamics between cells in the
targeted country and those in countries not targeted by a Pope speech irrelevant. For this reason,
we exploit an event-study estimation, which estimates the effect of the speech within cells located
in the targeted country, comparing the incidence of conflict events a few weeks before and after the
Pope’s peace-seeking message. Additionally, by accounting for country-specific and time-specific
variations through the inclusion of fixed effects, our approach ensures that the estimated effect of
the Pope’s speeches is not biased by pre-existing trends or contextual factors that independently
influence conflict levels. Identification relies on relative variations in conflict incidence after the
speech compared to before, within a given country, while accounting for time-invariant cell char-
acteristics and global shocks.
One potential concern about the validity of our empirical design remains: messages from the
Catholic leader can only credibly impact conflict dynamics if they reach local actors. We take this
concern seriously and provide systematic evidence of the reach of the papal speeches using original
data, as detailed in section 3.3, to carefully assess their local impact.
Event definition.
In the simplest case, an event is defined as a week in which a speech by the
Catholic Pope includes a peace-seeking message directed at a specific country. The 131 individual
peace-seeking messages presented in subsection 3.1 correspond to 128 country-week pairs in which
at least one speech addresses an ongoing conflict in that country. From there, we face three main
challenges and outline our strategies to address each.
First, major conflict events may prompt the Pope to deliver multiple peace-seeking speeches on
the same conflict, not only within the same week but also over several weeks. To account for this,
we group all speeches addressing the same country within a four-week period as a single treatment
and consider the entire period from the first to the last speech as treated. After applying this
grouping, we identify 119 speech events out of the 131 individual messages, meaning that 91% are
not repeated messages (given our four-week window definition). These speech events are defined
as the weeks during which a papal speech targets a country due to an ongoing conflict. Second,
papal speeches delivered outside this four-week window may still fall within a “pre-speech” or
“post-speech” period. We restrict our analysis to isolated speech events, defined as those occurring
within an event window where no other speeches mentioning the same country and conflict are
given in the five weeks before or eight weeks after.31 This restriction excludes 16 speech events
31We assess the sensitivity of our findings to alternative time windows around papal speeches (−5/+10, −8/+8,
and −10/+10). Some of these alternative specifications may involve a different set of speeches compared to our main
analysis. Additionally, we conduct a complementary test that retains the original set of speeches while varying the event
15


from the initial 119, ensuring that estimated effects can be attributed to a single speech event rather
than the cumulative influence of multiple interventions.32 It also allows for a proper examination
of the pre-speech period to confirm the absence of pre-trends. Third, as noted in subsection 3.1, 5%
of the Pope’s speeches are delivered during visits planned years in advance. These visits include
speeches specifically addressing the host country, which is the case for 3 conflict-related speech
events among the remaining 119. We exclude these speech events, as the visits likely influence
conflict dynamics through the security measures implemented to protect the Pope.
These steps, detailed further in Online Appendix B.3, result in a final sample of 100 speech
events—defined as (series of) weeks of papal peace-seeking speeches targeting a specific African
country, excluding those delivered during papal trips to Africa.
Summary statistics.
Our analysis covers 100 speeches, with 22 delivered under Pope John Paul
II, 23 under Benedict XVI, and 55 under Pope Francis. It spans 27 African countries and includes
slightly more than 7,300 cells over a 26-year period. In the five-week window before a Pope’s
speech, the probability of observing at least one conflict in a given cell is approximately 1.73%, with
a 0.57% likelihood for battles, 0.64% for low-intensity events, and 0.41% for religious conflicts. In
the eight weeks following the speech, this probability rises slightly to 1.77%, with battles remaining
at 0.57%, low-intensity events at 0.64%, and religious conflicts increasing to 0.46%.
3.3
Identifying assumptions
For papal speeches to influence local conflict dynamics, they must reach a local audience. Although
these messages reach local populations through numerous channels, we focus on those that are
observable and quantifiable. Specifically, we test three key assumptions: i) national media report
on papal speeches; ii) local Catholic institutions disseminate them; and iii) papal speeches shape
individual perceptions.
News covering the Pope’s speeches in national outlets.
We estimate whether the Pope’s speeches
appear in the national news of the targeted countries. To this end, we use all main African news-
papers available on Europresse and Factiva, covering 27 national newspapers from 13 countries,
with content accessible around the time of a papal speech addressing them. Specifically, we in-
vestigate whether the presence of articles mentioning the Pope, alongside at least one element of
conflict-related lexicon, increases in the days following a speech.33 Of the 4’900 articles collected,
34% mention conflict. We estimate the following event-study equation:
window length. Our results remain largely consistent (Online Appendix G.1).
32Note that the 16 events excluded from our baseline sample do not originate from a single country or year but cover
six countries and nine different years. Furthermore, for these 16 events, the level of violence observed before the speeches
is not significantly higher than that measured for the speeches included in the baseline sample – even for battles. If a
difference exists, it seems to indicate a slightly lower intensity.
33The following keywords are included in the conflict lexicon: conflict, peace, war, peace building, mediation, nego-
tiation, resolution, reconciliation, ceasefire, diplomacy, violence, hostility, humanitarian, disarmament, truce, tension,
crisis, victim, death, suffering, loss, grief, insecurity, justice, hope, trauma, injury. Keyword searches were conducted in
the languages of the newspapers: Arabic, English, French, Portuguese, and Spanish.
16


PopeNewsj,i,s,t =
9
∑
k=−9
βk . Posti,s,t+k + ωj,i,s + DoWt + ϵj,i,s,t
where j, i, s and t denote newspaper, country, event-window and date, respectively. For each
newspaper available at the time of a speech targeting its country, we include all days within a −14
to +14 day window around the speech. PopeNewsj,i,s,t is a dummy variable indicating whether
newspaper j contains at least one conflict-related article mentioning the Pope. Posti,s,t+k is a set
of dummy variables indicating whether the Pope delivered a peace-seeking speech mentioning
country i k days prior to date t + k, measured in 2-day intervals. We include newspaper-event
window fixed effects (ωj,i,s) to account for differences in newspapers’ propensity to cover the Pope
and other time-varying factors. Additionally, we include day-of-the-week fixed effects (DoWt) to
control for within-week seasonality in Papal coverage.
Figure 1: Coverage of Papal speeches in national media of targeted countries
-.02
0
.02
.04
.06
.08
Coefficient point estimates (90% CI)
-9
-7
-5
-3
-1
1
3
5
7
9
Distance to Pope's conflict speech
Note: The figure shows the daily average effects of the Pope’s speeches on national news coverage in the targeted
countries, using a 14-day pre-speech and 14-day post-speech event window with 2-day intervals. The omitted category
is t = −1, representing days -1 and -2 relative to the speech. The unit of observation is a national newspaper × date. The
dependent variable is a dummy indicating whether at least one article about the Pope’s speech appears. The specification
includes newspaper-event window fixed effects and day-of-the-week fixed effects. Standard errors are clustered at the
date level.
Estimates presented in Figure 1 show that the presence of news covering the Pope’s speech
rises significantly in national newspapers of the targeted country. This effect is substantial: in
the first two days following the speech, the probability increases by 5.1 percentage points (34% of
one standard deviation) and by 3.6 percentage points (24% of one standard deviation) on the two
following days. Notably, the effect is short-lived, with no pre-trend, suggesting that the increase is
directly driven by the timing of the Pope’s speech.
Diffusion of Papal Speeches by Local Religious Institutions.
To examine how papal speeches
spread through local Catholic institutions, and in the absence of data on the daily offline commu-
17


nications of dioceses, we leverage novel data from the Facebook activity of dioceses in our sample.
Specifically, we estimate a version of Equation 2, where the dependent variable is a dummy indi-
cating whether a post by a diocese in the targeted country mentions the Pope or contains at least
one element of conflict-related lexicon.
Figure 2: Coverage of papal speeches in Facebook posts by Catholic dioceses in targeted countries
-.06
-.04
-.02
0
.02
.04
.06
.08
.1
.12
Coefficient point estimates (90% CI)
-9
-7
-5
-3
-1
1
3
5
7
9
Distance to Pope's conflict speech
Note: The figure shows the daily average effects of the Pope’s speeches on the presence of papal messages in Facebook
posts by dioceses in the targeted countries, using a 14-day pre-speech and 14-day post-speech event window with 2-day
intervals. The omitted category is t = −1, representing days -1 and -2 relative to the speech. The unit of observation
is a diocese Facebook Page × date. The dependent variable is a dummy indicating whether at least one post about the
Pope’s speech appears. The specification includes diocese-event window fixed effects and day-of-the-week fixed effects.
Standard errors are clustered at the date level.
Figure 2 presents the results. The likelihood of a diocese in a target country posting about the
Pope’s speech on its Facebook page increases significantly, with a two-day lag. This effect is sub-
stantial: on the third and fourth days following the speech, the probability rises by 6.7 percentage
points (29% of one standard deviation) before gradually returning to pre-speech levels. As in the
newspaper analysis, the effect is short-lived, with no pre-trend, suggesting that the increase is in-
deed driven by the timing of the Pope’s speech. The lack of an effect in the first two days may be
due to the time dioceses need to process and post the relevant information, and unlike professional
media, which can publish immediately.
Pope’s speeches and individual perception.
Finally, we assess whether the Pope’s peace-seeking
messages resonate in the targeted countries by examining whether individuals–particularly Catholics–
adjust their perceptions of religious authority in response to these speeches. To investigate this, we
use individual-level data from Afrobarometer, a nationally representative survey across African
countries (see Depetris-Chauvin et al., 2020 and Hatte et al., 2025 for similar analyses). We focus
on three waves (5, 7, and 8), covering the years 2013 and 2017–2021, as these are the ones that pro-
vide information on the importance of religion in respondents’ lives, their trust in religious leaders,
18


their tolerance toward neighbours’ religions, and their perceived religious discrimination. Addi-
tionally, we use information on respondents’ characteristics, such as gender, age, and living area.
We estimate the following equation:
Rp,i,t,s = βPostp,i,t,s + µp + δD′
i,s + εp,i,t,s
where p, i, t and s denote respectively individual, country, date of the interview and event-
window. R is one of the attitudinal variables described previously. Postp,i,t equals to 1 if the re-
spondent was interviewed in the days following a Pope’s peace-seeking speech mentioning their
country, and 0 otherwise. The term µp is a vector of individual controls including age, age squared
and an indicator for living in urban area. The inclusion of country×speech fixed effects (D′
i,s) en-
sures that identification relies on comparing respondents interviewed after a given Pope speech
mentioning their country with those interviewed in the same country before that speech. Standard
errors are clustered at country × survey round.
Table 1 displays the results based on the sample of Christian respondents. These individuals
report a greater importance of religion in their lives and higher trust in religious leaders after the
Pope’s peace-seeking mentioning their country, with both effects ranging from approximately 2%
to 5% relative to the sample mean, similar to the effect of gender (not displayed but around 2%).
Note that we find no effect on non-Christian individuals, and similar results are found when using
a continuous measure (Online Appendix F).
Table 1: Pope speech and religious attitudes
Dummy:
Importance of
Trust in
Tolerance
Personal
religion
religious leader
discrimination
(1)
(2)
(3)
(4)
Post
0.022*
0.044*
–0.003
–0.029**
(0.010)
(0.024)
(0.018)
(0.013)
Observations
2265
4242
3708
5392
Mean dep. var.
0.96
0.83
0.84
0.19
Country × Speech FE
✓
✓
✓
✓
Note: The table presents the estimation of the effect of Pope Speeches on attitudinal variables regarding religion in
respondent’s lives. The sample includes respondents interviewed within 5 days before and after a Pope Speech. The
dependent variable equals 1 if the respondent declares finding religion somewhat or very important in their life (col. 1),
if they declare trusting somewhat or a lot religious leaders (col. 2), if they somewhat or strongly like having people of a
different religion as neighbours (col. 3), or if they have felt personally discriminated against at least once in the past year
because of their religion (col. 4), and 0 otherwise. Post is a binary indicator equal to 1 for weeks after a Pope’s speech.
Standard errors, clustered at the country × survey round, are in parentheses. *** p < 0.01, ** p < 0.05, * p < 0.1.
19


4
The dynamics of conflict following the Pope’s peace-seeking speeches
4.1
Pope’s speeches and conflict dynamics over time
We begin by analyzing the effect of the Pope’s speeches on conflict incidence over time in the tar-
geted country’s geographic cells, and report the results in an event-study graph. This methodology
allows us to systematically track variations in conflict levels before and after the speeches, offering
insights into the timing and duration of the treatment effect, and potential pre-trends. Figure 3
presents the estimated coefficients, which represent the average effect of the Pope’s speeches on
conflict incidence for each week relative to the week before the speech (t = -1). Additionally, we
report the mean effects and their respective confidence intervals for four pooled time periods: t ∈
[-5, -2], t ∈[0, 2], t ∈[3, 5], and t ∈[6, 8].34
Figure 3: Average effect of Pope speeches on conflict: Event study graph
-1.5
-1
-.5
0
.5
Average effect (90% CI)
-5
-4
-3
-2
-1
0
1
2
3
4
5
6
7
8
Weeks since the pope's speech
Note: The figure shows the weekly average effects of Pope Speeches on the incidence of conflict within a 5-week pre-
speech and 8-week post-speech event window. The unit of observation is a cell × week-year dyad. The sample includes
100 events, defined as papal peace-seeking speeches targeting a given African country outside of papal trips to Africa.
Each event window spans from 5 weeks before to 8 weeks after the Pope’s speech. The dependent variable equals
100 if at least one conflict event occurs in the cell during the week, 0 otherwise. The omitted category is t = −1, and
the shaded areas represent 90% confidence intervals. Red regions represent aggregated pre- and post-speech periods.
Baseline FEs encompasses cell, event-window-by-country ([−5; +8] weeks around a speech targeting a given country),
and week-of-year fixed effects. Standard errors are clustered at the cell level.
Reassuringly, the estimates for the pre-speech weeks confirm the absence of pre-trends. The
point estimates for the weeks preceding the speech are close to zero and statistically insignificant.
34The reported averages of the weekly estimated coefficients and their standard errors are computed using a non-linear
combination of the individual variances and covariances of these coefficients.
20


This pattern also holds when considering the mean effect over the entire pre-speech period (t ∈
[-5, -2]). Crucially, the absence of pre-trends mitigates the risk of mean reversion, where conflict
levels might naturally decline following periods of high intensity due to cyclical patterns, seasonal
influences, or broader temporal trends. This strengthens the validity of our setting, suggesting
that any observed post-speech changes in conflict levels are unlikely to be driven by confounding
factors or pre-existing dynamics.
In the post-speech period, the results indicate a clear and immediate decline in conflict inci-
dence, with a substantial quantitative impact. In the first week after the speech, the probability
of violence decreases by 40%, while in the second and third weeks, the reduction ranges between
18% and 22%. The pronounced effect in the first week, which diminishes by half in the subsequent
week but remains statistically significant, aligns with findings in the media literature documenting
short-term impacts following widespread coverage on various behaviors and attitudes (DellaVi-
gna and La Ferrara, 2015). On average, conflict incidence decreases by approximately 27% over
the three weeks following a papal speech.35 Although estimated with less precision, the findings
suggest a lasting effect of papal speeches. While point estimates remain relatively stable over time,
standard errors increase, indicating greater variability in later periods. This variability may reflect
differences in speech effectiveness across contexts and regions, motivating further analysis in the
remainder of the paper.
4.2
Baseline estimates
Impact of papal speeches on conflict incidence and violence types.
Table 2 presents the base-
line estimates from Equation 1. The results indicate a significant decline in violence in the weeks
following a papal speech (col. 1). Consistent with Figure 3, conflict incidence decreases by an av-
erage of 23% over the eight weeks after a speech. Disaggregating by violence type reveals notable
patterns. Battles decrease by 27% (p-value = 0.102; col. 2), while low-intensity events decline by
34% (col. 3). These findings suggest that papal speeches effectively reduce various forms of vi-
olence, supporting the hypothesis that external shocks—such as public messaging by influential
leaders—can shape local conflict dynamics by influencing beliefs and norms. The stronger impact
on low-intensity events suggests that papal interventions may be particularly effective in mitigat-
ing smaller-scale conflicts, where moral authority and rhetorical influence have a more immediate
and localized effect. Such events often occur in fragmented violence contexts, where structural
factors like resource competition or territorial control play a lesser role (Blattman, 2022; Acemoglu
et al., 2001). In contrast, large-scale violent events are typically driven by entrenched political inter-
ests, economic incentives, or the strategic objectives of organized armed groups, making them less
susceptible to moral persuasion. Another critical dimension of the Pope’s influence is his ability
to mitigate religiously motivated violence. Despite imprecise estimates, our analysis suggests that
papal speeches tend to reduce the likelihood of religiously motivated conflicts (col. 4).36
35The average point estimate for t ∈[0,2] is −0.4667, while the pre-speech sample mean of conflict is 1.734.
36Along with testing the sensitivity of our findings to different time windows around papal speeches (Online Ap-
pendix G.1), we demonstrate that our results are not driven by any specific country or year (Online Appendix G.2).
21


Table 2: Average effect of papal speeches on different categories of conflict
Dependent variable:
Conflict incidence, by type of events:
All
Battles
Low intensity
Religious
(1)
(2)
(3)
(4)
Post
–0.409**
–0.153
–0.218**
–0.118
(0.165)
(0.093)
(0.105)
(0.101)
Observations
473802
473802
473802
473802
Mean dep. var.
1.76
0.57
0.64
0.44
Baseline FEs
✓
✓
✓
✓
Note: The table presents the estimation of the effect of Pope Speeches on the incidence of different conflict types. The
unit of observation is a cell × week-year dyad. The sample includes 100 events, defined as papal peace-seeking speeches
targeting a given African country outside of papal trips to Africa. Each event window spans from 5 weeks before to 8
weeks after the Pope’s speech. The dependent variable equals 100 if at least one conflict event occurs in the cell during
the week: any conflict (col. 1), battle (col. 2), protest/riot (col. 3), or religion-related conflict (col. 4), and 0 otherwise.
Post is a binary indicator equal to 1 for weeks after a Pope’s speech. Baseline FEs encompasses cell, event-window-by-
country ([−5; +8] weeks around a speech targeting a given country), and week-of-year fixed effects. Standard errors,
clustered at the cell level, are in parentheses. *** p < 0.01, ** p < 0.05, * p < 0.1.
Differences in impact by Pope and the Regensburg speech.
Building on Section 2.2 and the
observation that the three Popes in our analysis adopted distinct ideological leanings, particularly
regarding Africa, we examine how the effects of their speeches vary based on the identity of the
Pope delivering them. To achieve this, we modify Equation 1 by decomposing the Post variable
into three dummies, each representing the Post period for one of the three Popes. Panel A of Table
3 presents the results.
Speeches by John Paul II and Francis are associated with significant reductions in overall con-
flict incidence, with decreases of 89.5% and 21%, respectively. For John Paul II, the reduction is con-
centrated in battles (113%), with no significant effects observed for low-intensity or religiously mo-
tivated events. In contrast, Francis’ speeches exhibit a broader impact, significantly reducing bat-
tles (29.6%) and low-intensity events (32.5%). These differences underscore the distinct leadership
styles and rhetorical approaches of the two Popes: John Paul II, whose papacy emphasized inter-
state peace (John Paul II, 1995; see Subsection 2.2), had a pronounced effect on reducing battles,
while Francis, with his grassroots engagement, influenced a wider range of conflict dynamics. This
contrast aligns with prior research on religious leadership in Africa, which highlights how leaders’
influence depends on their ability to engage with both political institutions and broader civil society
(Ellis and ter Haar, 1998). While John Paul II’s papacy emphasized institutional diplomacy, Fran-
cis’ broader social engagement aligns with findings on how religious leaders shape public norms
through direct social interaction (Freston, 2001). The estimated effects of Papal speeches on reli-
giously motivated conflicts are negative but imprecisely estimated for these two Popes. However,
when considering the combined effect of John Paul II and Francis, we observe a significant nega-
22


tive impact of considerable magnitude, with their speeches reducing the probability of religiously
motivated conflict by 34.3% (p-value = 0.077).
The results for Benedict XVI, however, present a more nuanced picture. While his speeches
show no overall effect on conflict dynamics (col. 1), a closer examination reveals significant varia-
tion across conflict types. Specifically, we find no impact on low-intensity events, but his speeches
are associated with a substantial increase in battles (85.8%) and religiously motivated violence
(60%). Benedict XVI’s papacy was characterized by theological conservatism, an emphasis on tradi-
tional Church values, and a more limited engagement with Africa. His doctrinal stance frequently
sparked controversy in culturally diverse regions, as illustrated by two major incidents: his op-
position to condom use during the AIDS crisis in Cameroon and the widely debated Regensburg
speech. Delivered in 2006, the Regensburg speech contained remarks that were widely perceived
as critical of Islam, triggering significant backlash across Muslim-majority countries and beyond.
Given the polarizing nature of this speech and its potential to shape perceptions of Benedict XVI’s
papacy, we investigate whether it represented a turning point in the impact of his messages on
conflict dynamics.
Panel B of Table 3 presents results distinguishing between speeches delivered before (6 distinct
speeches) and after the Regensburg speech (17 distinct speeches). Although imprecisely estimated,
the effects of Benedict XVI’s speeches prior to the Regensburg address is negative (col. 1). The
reduction is better estimated for low-intensity violence (p-value = 0.121), where we observe a sub-
stantial decrease of nearly 84%. In contrast, following the Regensburg speech, we estimate a sharp
and significant increase in battles and religious violence. While other aspects of Benedict XVI’s
papacy may have contributed to these shifts in conflict dynamics, the clear divergence in effects
before and after the Regensburg speech suggests that this speech played a critical role in shaping
his broader influence on violent conflicts.
4.3
Distinctive impact of papal speeches and UN conflict resolutions
One might question whether our findings can be extrapolated and remain quantitatively similar
when an institution, widely recognized as leaders in peacekeeping, adopts a position on an armed
conflict. To explore this, we examine one major institution that actively advocates for and inter-
venes in conflicts: the United Nations.37
The UN provides a well-documented, structured, and extensive set of resolutions that address
conflicts worldwide, allowing for a rigorous evaluation of their impact on conflict dynamics. We
collected all resolutions published by the UN Security Council from 1997 to 2022. As the primary
UN body responsible for maintaining international peace and security, the Security Council has the
authority to adopt binding resolutions, impose sanctions, and authorize peacekeeping operations.
Its resolutions play a critical role in conflict prevention, peacekeeping, and post-conflict reconstruc-
37Ideally, testing this hypothesis would require collecting speeches and official statements from a broad range of po-
litical and institutional leaders, including regional African organizations, heads of state, and other international actors.
However, assembling a comprehensive and systematically comparable dataset across multiple speakers presents signif-
icant challenges, particularly in terms of consistency and availability of conflict-related positions. For this reason, we
focus on UN resolutions.
23


Table 3: Decomposing post-speech effects by individual Pope
Dependent variable:
Conflict incidence, by type of events:
All
Battles
Low intensity
Religious
(1)
(2)
(3)
(4)
Panel A: Heterogeneity by Pope
Post: John Paul II
–0.519**
–0.386*
0.063
–0.161
(0.246)
(0.204)
(0.054)
(0.127)
Post: Benedict XVI
0.130
0.292*
–0.028
0.144*
(0.221)
(0.149)
(0.089)
(0.086)
Post: Francis
–0.535**
–0.222*
–0.338**
–0.181
(0.236)
(0.124)
(0.157)
(0.150)
Observations
473802
473802
473802
473802
Mean dep. var. John Paul II
0.58
0.34
0.07
0.05
Mean dep. var. BenedictXVI
0.83
0.34
0.16
0.24
Mean dep. var. Francis
2.56
0.75
1.04
0.66
Post: John Paul II ̸= Benedict XVI
0.05
0.01
0.41
0.05
Post: John Paul II ̸= Francis
0.96
0.49
0.01
0.92
Post: Benedict XVI ̸= Francis
0.04
0.01
0.09
0.06
Panel B: Benedict XVI’s Regensburg Speech
Post: John Paul II
–0.519**
–0.386*
0.063
–0.161
(0.246)
(0.204)
(0.054)
(0.127)
Post: Benedict XVI pre Regensburg
–0.117
0.004
–0.134
0.000
(0.375)
(0.193)
(0.087)
(0.000)
Post: Benedict XVI post Regensburg
0.240
0.420**
0.019
0.209*
(0.272)
(0.198)
(0.123)
(0.125)
Post: Francis
–0.535**
–0.222*
–0.338**
–0.181
(0.236)
(0.124)
(0.157)
(0.150)
Observations
473802
473802
473802
473802
Mean dep. var. John Paul II
0.58
0.34
0.07
0.05
Mean dep. var. BenedictXVI
0.83
0.34
0.16
0.24
Mean dep. var. Francis
2.56
0.75
1.04
0.66
Baseline FEs
✓
✓
✓
✓
Note: The table presents the estimation of the heterogeneous effect of Pope Speeches on the incidence of different conflict
types. The unit of observation is a cell × week-year dyad. The sample includes 100 events, defined as papal peace-
seeking speeches targeting a given African country outside of papal trips to Africa. Each event window spans from 5
weeks before to 8 weeks after the Pope’s speech. The dependent variable equals 100 if at least one conflict event occurs
in the cell during the week: any conflict (col. 1), battle (col. 2), protest/riot (col. 3), or religion-related conflict (col. 4),
and 0 otherwise. In Panel A, Post: John Paul II, Post: Benedict XVI, and Post: Francis are binary indicators equal to 1 for
weeks following a speech by the respective Pope. In Panel B, Post: Benedict XVI is divided in two periods pre and post
Regensburg speech (12/09/2006). Baseline FEs encompasses cell, event-window-by-country ([−5; +8] weeks around
a speech targeting a given country), and week-of-year fixed effects.Standard errors, clustered at the cell level, are in
parentheses. *** p < 0.01, ** p < 0.05, * p < 0.1.
24


tion worldwide.38 Following the same procedure used to define an event for papal speeches, we
identify 215 resolution-based events, defined as UN Security Council peace-seeking resolutions
targeting a specific African country.39
First, we assess whether UN Security Council peace-seeking resolutions targeting a specific
African country are widely disseminated and acknowledged within the mentioned countries. The
likelihood of news articles mentioning the United Nations Security Council increases significantly
in the country targeted by the resolution (Figure D5, Online Appendix D). The effect is short-lived
but substantial, though 24% smaller in magnitude than the impact of papal speeches.40 Second, we
estimate Equation 1 with UN Security Council resolutions. We find a negative but non-significant
effect on overall violence, battles, and religious events, while the effect on low-intensity violence is
positive (Table 4).
While both papal speeches and UN Security Council resolutions are disseminated by African
local media, as evidenced by printed press coverage, only papal speeches exhibit a statistically
significant impact on conflict dynamics. This suggests a fundamental difference in how religious
and political institutions influence conflict, with religious discourse potentially shaping behavioral
responses in a more nuanced and profound manner. The unique impact of papal speeches aligns
with broader research on religious institutions, which emphasizes their role in shaping social norms
and political stability through moral authority rather than formal enforcement mechanisms (Ian-
naccone, 1998; McCleary and Barro, 2006).
5
Mechanisms
This section investigates the potential mechanisms through which the Pope’s messages influence
violence dynamics. We focus on three primary channels: local religious communities, local reli-
gious institutions, and interactions with political leaders and armed groups. Specifically, our anal-
ysis explores the presence of Christian communities and the attributes of local Catholic bishops,
examining their ideological alignment with the Pope and their diverse experiences both within the
broader Catholic Church and in their specific local contexts. Additionally, we analyze the inter-
actions between papal messages and key actors–including political leaders and armed groups–to
unpack the complex institutional and strategic dynamics that may mediate their impact on conflict.
While our analysis focuses on these channels, we acknowledge the potential for other mechanisms
to influence the dynamics.
38The resolutions are available at the UN Security Council website. The Security Council consists of 15 member states,
including five permanent members with veto power–China, France, Russia, the United Kingdom, and the United States–
and ten rotating members elected for two-year terms.
39We identify 771 resolutions mentioning at least one African country, accounting for 899 resolution×country observa-
tions. We then apply the exact same procedure used for papal speeches to define an event: i) we group all resolutions tar-
geting the same country within a four-week period as a single treatment; ii) we focus only on isolated resolutions—those
published within an event window containing no other resolutions mentioning the same country and conflict in the five
weeks prior or eight weeks after the resolution. These steps yield a final sample of 215 events. Online Appendix D
provides more details on this procedure.
40On the same day, the probability of news coverage of the UN resolution rises by 5.4 percentage points–29% of one
standard deviation–in the targeted country, while in Section 3.3 we document an increase in news coverage of 36% of a
standard deviation the same day of a papal speech.
25


Table 4: Average effect of UN Security Council resolutions on categories of conflict
Dependent variable:
Conflict incidence, by type of events:
All
Battles
Low intensity
Religious
(1)
(2)
(3)
(4)
Post
–0.073
–0.029
0.003
–0.015
(0.080)
(0.051)
(0.041)
(0.031)
Observations
663579
663579
663579
663579
Mean dep. var.
1.15
0.48
0.30
0.17
Baseline FEs
✓
✓
✓
✓
Note: The table presents the estimation of the effect of UN Security Council resolutions on the incidence of different
conflict types. The unit of observation is a cell × week-year dyad. The sample includes 215 events, defined as UN
Secretary General peace-seeking resolutions targeting a given African country. Each event window spans from 5 weeks
before to 8 weeks after the Pope’s speech. The dependent variable equals 100 if at least one conflict event occurs in the
cell during the week: any conflict (col. 1), battle (col. 2), protest/riot (col. 3), or religion-related conflict (col. 4), and
0 otherwise. Post is a binary indicator equal to 1 for weeks after a the publication of a UN Security Council resolution.
Baseline FEs encompasses cell, event-window-by-country ([−5; +8] weeks around a speech targeting a given country),
and week-of-year fixed effects. Standard errors, clustered at the cell level, are in parentheses. *** p < 0.01, ** p < 0.05, *
p < 0.1.
5.1
Local presence of religious communities
The impact of papal speeches on violence dynamics likely depends on the local presence of reli-
gious communities. Shared religious identity among Christians should foster receptiveness, while
the Catholic Church’s institutional networks can also facilitate the dissemination of the Pope’s mes-
sage. In conflict environments, both can enhance social cohesion and unity (Bassi and Rasul, 2017;
Wang, 2021).
We replicate Table 2, restricting the sample to cells where Christian places of worship are
recorded (see Section 3.1 for more details). Note that our focus on Christian communities, rather
than specifically Catholic ones, is driven by the lack of a clear distinction between Catholic and
other Christian places of worship in the data. This is likely not a major concern, as the influence of
the Catholic Pope extends to the broader Christian community (John Paul II, 1995).41 We estimate
a significant reduction in violence in the weeks following a papal speech (Table 5, col. 1). Quan-
titatively, violence decreases by 33.5%, a magnitude 46% larger than that reported in our baseline
(Table 2, col. 1). While the effect of the Pope’s speeches on battles is imprecisely estimated (col. 2),
they significantly reduce low-intensity violence by 48% in the weeks following the speech (col. 3).
41In this encyclical, John Paul II emphasizes the Catholic Church’s commitment to fostering unity among all Christians,
highlighting the importance of ecumenical dialogue and collaboration with other Christian denominations. Other key
examples in ecumenical dialogue include the Second Vatican Council (1965, in particular the Unitatis Redintegratio, 1964,
i.e. the Decree on Ecumenism), during which Pope Paul VI and Orthodox Patriarch Athenagoras I lifted the mutual
excommunications, and the 1999 Joint Declaration on the Doctrine of Justification, signed by the Catholic Church and
the Lutheran World Federation, which underscored the Pope’s influence in advancing Christian unity.
26


Notably, in areas with a Christian presence, there is a significant decline in religiously related events
(col. 4), an effect that was imprecisely estimated in the overall sample. Consistent with the con-
ceptual framework, which suggests that peace efforts are more effective when aligned with local
institutions and existing belief systems (Blattman, 2022), this reduction is substantial: following the
Pope’s speech, the probability of religious violence decreases by 69%.42 Taken together, and com-
pared with the magnitudes estimated in Table 2, changes in violence are primarily concentrated
in areas with Christian religious communities. This conclusion is reinforced by the absence of ef-
fects in cells without Christian communities, except for a notable rise in low-intensity events (Table
I13 in Appendix I). In the following exercises, we limit the analysis to grid cells with documented
Christian places of worship.
Table 5: Impact of papal speeches on violence in regions with Christian places of worship
Dependent variable:
Conflict incidence, by type of events:
All
Battles
Low intensity
Religious
(1)
(2)
(3)
(4)
Post
–1.370***
–0.383
–0.836**
–0.674**
(0.475)
(0.268)
(0.329)
(0.305)
Observations
159246
159246
159246
159246
Mean dep. var.
4.09
1.21
1.75
0.97
Baseline FEs
✓
✓
✓
✓
Note: The table presents the estimation of the effect of Pope Speeches on the incidence of different conflict types. The
unit of observation is a cell × week-year dyad. The sample includes 100 events, defined as papal peace-seeking speeches
targeting a given African country outside of papal trips to Africa and observations are restricted to cells where Christian
places of worship are recorded. Each event window spans from 5 weeks before to 8 weeks after the Pope’s speech. The
dependent variable equals 100 if at least one conflict event occurs in the cell during the week: any conflict (col. 1), battle
(col. 2), protest/riot (col. 3), or religion-related conflict (col. 4), and 0 otherwise. Post is a binary indicator equal to 1 for
weeks after a Pope’s speech. Baseline FEs encompasses cell, event-window-by-country ([−5; +8] weeks around a speech
targeting a given country), and week-of-year fixed effects.Standard errors, clustered at the cell level, are in parentheses.
*** p < 0.01, ** p < 0.05, * p < 0.1.
5.2
Local religious institutions and the dissemination of the peace message
The Catholic Church relies on local institutions, particularly in unstable regions, with bishops serv-
ing as key intermediaries between the Holy See and local communities (Second Vatican Council,
1965). Recent studies highlight their role in navigating socio-political complexities while advancing
the Church’s broader mission (O’Malley, 2008). Beyond their spiritual role, bishops guide dioce-
san activities and facilitate dialogue in conflict zones. Their influence depends on two key factors:
42Table I12 in Online Appendix I.1 shows that speeches by John Paul II and Francis reduce conflict, with John Paul
II having a stronger impact, particularly on battles. In contrast, Benedict XVI’s speeches increase battles and religious
violence while having no overall significant effect. Francis notably reduces battles, low-intensity events, and religious
violence.
27


alignment with the Pope’s agenda and experience within the Church and their dioceses. This sub-
section examines how these factors shape the impact of papal speeches on local conflict dynamics.43
Measuring bishops’ ideological alignment with the Pope.
We expect bishops ideologically aligned
with the Pope to be more effective in disseminating his peace message. To approximate this align-
ment, we leverage variation in the timing of bishops’ appointments.44 The appointment process is
complex and reflects the Church’s hierarchical structure (see Online Appendix H for details). While
multiple stakeholders—retired bishops, neighboring dioceses, the faithful, the apostolic nuncio,
and Roman Curia dicasteries—contribute to the selection, the final decision rests with the Pope,
in line with canonical tradition established by the Pio-Benedictine Code of 1917 and subsequent
canon law revisions (Vatican Press, 1917; Second Vatican Council, 1965). While some bishops may
share the current Pope’s ideological views, others may have been appointed by predecessors with
different leanings. We define a dummy variable (aligned appointment) equal to 1 if the bishop was
appointed by the Pope delivering the speech.
Bishops’ experience overall, and tenure duration locally.
A bishop’s leadership effectiveness
fundamentally depends on their ability to build trust and institutional networks, both within the
Church and locally. Without established credibility, leaders may require significant time to de-
velop crucial ties, underscoring the importance of institutional alignment in effective leadership
(Hodler and Raschky, 2014; Burgess et al., 2015). This dynamic is especially pronounced in conflict
settings, where a bishop’s local connections and contextual knowledge can substantially influence
peacebuilding efforts. Long tenure enables leaders to comprehend the socio-political landscape,
cultivate networks, and establish trust. Empirical evidence demonstrates that experience enhances
leaders’ capacity to address local challenges (Becker and Woessmann, 2009; Barro, 2004; Chambru,
2019) and mitigate violence while promoting peace (Acemoglu et al., 2001).
We define two distinct measures of experience. Overall experience captures the number of years
since a bishop’s ordination as a priest, reflecting their general ecclesiastical background. Local ex-
perience measures the duration of a bishop’s tenure within a specific diocese, calculated from their
arrival to the date of the papal speech. Local experience is particularly critical for conflict medi-
ation, as long-tenured bishops develop a nuanced understanding of local political and religious
dynamics. This includes insights into relationships with non-Catholic leaders and the intricate
sources of tension among armed groups. However, extended tenure can potentially diminish a
bishop’s effectiveness if they have previously aligned with a conflicting party.45
Estimated contributions of local religious institutions in the nexus between papal speeches and
conflict dynamics.
To estimate the role of bishops’ characteristics, we extend Equation 1 by inter-
43We restrict the sample to cells with bishops who do not change in the 5 weeks before and 8 weeks after the speech.
This reduces the sample by 13.8%, but the restriction does not significantly bias the selection toward specific countries
or regions.
44This methodology is also adopted in Martinez-Bravo et al. (2025).
45Ideally, we would have comprehensive data on bishops’ relationships with local actors or their conflict positions,
but such information is not available.
28


acting the variable Post with the three measures defined above. We also saturate the model with
an event-window × bishop fixed effect. Table 6 presents the estimates. The measures of experi-
ence are centered, so the Post variable represents the effect of a Pope’s speech when the bishop was
not appointed by the Pope delivering the speech, and for average levels of both local and overall
experience.46
Several key results emerge. First, ideological alignment matters: the Pope’s message is 17%
more effective when relayed by a bishop appointed by the same Pope, compared to one appointed
by a predecessor. Second, regarding experience, an intriguing finding is that local experience does
not appear to be a crucial factor, while overall experience has a quantitatively significant effect (col.
1). For every additional year of overall experience, conflict incidence decreases by 1% after a papal
speech. The reduction in violence associated with overall experience is significant for low-intensity
(1.16%) and religious conflict events (2.1%).47 We find also that ideological alignment and local
experience produce imprecise estimates for battles (col. 2).
Legacy of bishops’ appointments.
As shown in Tables 2 and 5, we find a difference in the effec-
tiveness of speeches delivered by Pope John Paul II compared to those of Pope Francis. Interest-
ingly, Francis’s speeches followed those of Benedict XVI, whose peace-seeking messages in Africa
were largely ineffective (if not counter-productive) during his tenure. This raises a natural question:
Could the lower effectiveness of Pope Francis’s speeches be partially attributed to Benedict XVI’s
legacy, particularly through bishops appointed during his papacy? To investigate this, while de-
manding, we focus exclusively on Francis’s speeches and estimate their differential impacts based
on whether the bishops were appointed by John Paul II, Benedict XVI, or Francis (Table 7).
The results reveal that when a bishop was appointed by Pope Francis, conflict incidence de-
creases by 34% (Post coefficient, col. 1). However, in cells where the bishop was appointed by
Benedict XVI, the reduction is 11 percentage points smaller (p-value ≈0.13), suggesting that Fran-
cis’s speeches are notably less effective in these regions.48 Although bishops appointed by Bene-
dict XVI have, on average and mechanically, greater local experience (7.9 years) compared to those
appointed by Francis (less than 4 years), overall experience is similar among the two groups of
bishops (31.5 years for those appointed by Benedict XVI and 30.5 for those appointed by Fran-
cis). Controlling for both local experience (col. 2) and overall experience (col. 3) reveals a persistent
12 percentage-point difference in effectiveness. This indicates that the weaker impact of Fran-
cis’s speeches in these regions likely reflects a broader legacy effect associated with Benedict’s
appointees. Interestingly, when comparing the impact of Francis’s speeches in cells with bish-
ops appointed by John Paul II versus those appointed by Francis, the initial effect appears similar.
However, after accounting for experience (cols. 2 and 3), a 7 percentage-point difference emerges,
46In this estimation sample, we have data for 400 bishops in 296 dioceses. The average overall experience is 34 years,
with a standard deviation of 9 years, while the average local experience is 11 years, with a standard deviation of 8.6 years.
47The role of overall experience in decreasing conflict is confirmed in areas with bishops nominated by John Paul II
(despite not precisely estimated) and for Francis (1%), while local experience has a significant effect in decreasing conflict
incidence in areas with bishops nominated by Pope Benedict (3.3%). See Table I14 in Online Appendix I.1 for details.
48The 11 percentage-point difference is calculated by comparing the effect in regions with bishops appointed by Francis
((-1.949 / 5.72)×100 = 34.07%) to those appointed by Benedict ((-1.949 + 0.635)/5.72)×100 = 22.9%). The estimated effects
in cells with Benedict’s appointees are somewhat imprecise (p-values between 0.17 and 0.19).
29


Table 6: How local church leadership shapes the effect of papal speeches on conflict
Dependent variable:
Conflict incidence, by type of events:
All
Battles
Low intensity
Religious
(1)
(2)
(3)
(4)
Post
–0.742
–0.555*
–0.636
–0.414
(0.572)
(0.335)
(0.395)
(0.310)
× Aligned appointment
–0.632*
0.007
–0.107
0.031
(0.342)
(0.194)
(0.245)
(0.153)
× Local experience
–0.016
–0.011
–0.000
0.008
(0.019)
(0.012)
(0.013)
(0.007)
× Overall experience
–0.038**
–0.007
–0.019*
–0.015**
(0.016)
(0.009)
(0.010)
(0.007)
Observations
137201
137201
137201
137201
Mean dep. var.
3.79
1.08
1.63
0.71
Baseline FEs
✓
✓
✓
✓
Event-window × bishop FEs
✓
✓
✓
✓
Note: The table presents the estimation of the effect of the Pope’s local institutions on the incidence of different conflict
types. The unit of observation is a cell × week-year dyad. The sample includes 100 events, defined as papal peace-
seeking speeches targeting a given African country outside of papal trips to Africa and observations are restricted to
cells where Christian places of worship are recorded. Each event window spans from 5 weeks before to 8 weeks after
the Pope’s speech. The dependent variable equals 100 if at least one conflict event occurs in the cell during the week:
any conflict (col. 1), battle (col. 2), protest/riot (col. 3), or religion-related conflict (col. 4), and 0 otherwise. Post is a
binary indicator equal to 1 for weeks after a Pope’s speech. Aligned appointment is a binary indicator equal to 1 if the
bishop was appointed by the Pope delivering the speech. Overall experience is the number of years since a bishop was
ordained as a priest. Local experience is the number of years between the arrival of the bishop in the diocese and the
date of the Pope’s speech. The three measures are interacted with the variable Post. Baseline FEs encompasses cell,
event-window-by-country ([−5; +8] weeks around a speech targeting a given country), and week-of-year fixed effects.
We saturate the model with an event-window-by-country × bishop fixed effect. Standard errors, clustered at the cell
level, are in parentheses. *** p < 0.01, ** p < 0.05, * p < 0.1.
30


suggesting that Francis’s speeches are slightly more effective where bishops were appointed by
him compared to those appointed by John Paul II.
Taken together, these results underscore the critical importance of alignment between papal
appointments and papal messages. Francis’s speeches prove most effective when relayed by bish-
ops he appointed. Moreover, the legacy effect of Benedict’s appointees appears more pronounced
than that of John Paul II’s appointees, potentially contributing to the lower overall effectiveness of
Francis’s speeches compared to those of his predecessor.
Table 7: Legacy effects of bishop appointments on the impact of Pope Francis’s speeches
Dependent variable:
Conflict incidence
(1)
(2)
(3)
Post
–1.949**
–2.086**
–2.119**
(0.948)
(1.012)
(1.013)
× Nominated by Benedict XVI
0.635
0.728
0.686
(0.458)
(0.535)
(0.534)
× Nominated by John Paul II
0.030
0.337
0.366
(0.417)
(0.935)
(0.936)
× Local experience
–0.018
0.017
(0.053)
(0.053)
× Overall experience
–8.480**
(3.814)
Observations
74517
74517
74517
Mean dep. var.
5.71
5.71
5.71
Baseline FEs
✓
✓
✓
Event-window × bishop FEs
✓
✓
✓
Note: The table presents the estimation of the effect of the Pope’s legacy and local institutions on the incidence of conflict.
The unit of observation is a cell × week-year dyad. The sample includes 52 events, defined as papal peace-seeking
speeches targeting a given African country outside of papal trips to Africa under Francis’ pontificate, and observations
are restricted to cells where Christian places of worship are recorded. Each event window spans from 5 weeks before to
8 weeks after the Pope’s speech. The dependent variable equals 100 if at least one conflict event occurs in the cell during
the week, and 0 otherwise. Post is a binary indicator equal to 1 for weeks after a Pope’s speech. Nominated by Benedict XVI
and Nominated by John Paul II are binary indicators equal to 1 if the bishop was appointed by Benedict XVI or John Paul
II, respectively. Overall experience is the number of years since a bishop was ordained as a priest. Local experience is the
number of years between the arrival of the bishop in the diocese and the date of the Pope’s speech. The four measures
are interacted with the variable Post. Baseline FEs encompasses cell, event-window-by-country ([−5; +8] weeks around
a speech targeting a given country), and week-of-year fixed effects. We saturate the model with an event-window-by-
country × bishop fixed effect. Standard errors, clustered at the cell level, are in parentheses. *** p < 0.01, ** p < 0.05, * p
< 0.1.
5.3
“World is watching”: The role of political leader
Another important dimension concerns the role of political leaders following a papal speech. As
discussed in Sections 2 and 3.3, the Pope’s message is universal and widely disseminated, partic-
31


ularly through national media. Consequently, when a country is mentioned in a papal speech, it
comes under global scrutiny and attracts significant international attention. In this context, the
country’s political leader may feel prompted to take action to reduce tensions and violence. How-
ever, in the African context, political leaders tend to exert the most influence in their regions of
birth (Franck and Rainer, 2012; Hodler and Raschky, 2014; Burgess et al., 2015). Thus, we estimate
whether, following the Pope’s speech, violence dynamics differ in the leader’s birthplace regions
compared to other regions. Table 8 presents the results.
When considering all events, we find no significant differences in conflict dynamics between
cells in the leader’s birthplace region and those in other regions in the weeks following the Pope’s
speech (col. 1). This result is similar for battles as well (col. 2). However, significant differences
emerge for low-intensity events and events with a religious dimension. For low-intensity events,
violence decreases by 71% in cells within the leader’s birthplace region compared to a 45% reduc-
tion in cells in other regions (col. 3). This significant difference is also observed for religiously
motivated events, where the probability of violence decreases by 87% in cells of the leader’s birth-
place region compared to a 67% reduction in other regions (col. 4). These findings highlight the
importance of the Pope’s speech in shaping national political dynamics and suggest that it can
serve as a mechanism for reducing violence.49
5.4
The role of armed groups
So far, our analysis has examined conflict without distinguishing between the armed groups in-
volved. However, the different actors engaged may respond differently to the Pope’s call for peace.
We explore two key dimensions that may influence these responses.
First, as noted in Section 2, an armed group’s reaction may depend on whether they have a
religious affiliation. Religious and non-religious armed groups might interpret the Pope’s message
differently, influencing their willingness to de-escalate violence. Second, the level of pre-existing vi-
olence between two armed groups can shape the impact of the peace-seeking speech. When conflict
between groups is already high, the effects are ambiguous. On one hand, violence may decrease
for several reasons. Prolonged conflict imposes significant human, material, and reputational costs
that armed groups may seek to avoid. The Pope’s speech could act as a focal point for reconsider-
ing alternatives to violence, consistent with research on how peace-promoting interventions reduce
uncertainty and facilitate coordination among conflicting parties (Fearon, 1995; Sawyer, 2004). Ad-
ditionally, groups engaged in intense violence may face growing pressure from local communities,
national authorities, or external supporters to de-escalate following the Pope’s intervention. On the
other hand, conflict escalation in response to the Pope’s speech is also possible. If a group perceives
bias, they may intensify violence to counteract it or signal their strength. The speech could deepen
divisions, provoke backlash, or be strategically exploited—such as one group using a ceasefire to
gain an advantage. This aligns with findings on how external interventions can sometimes shift
49Table I15 in Online Appendix I.3 presents the results differentiated by the Pope delivering the speech. Significant
differences are observed for John Paul II for low intensity conflict, while no significant differences are identified for Pope
Benedict nor Pope Francis.
32


Table 8: Local political influence and the impact of papal speeches on conflict dynamics
Dependent variable:
Conflict incidence, by type of events:
All
Battles
Low intensity
Religious
(1)
(2)
(3)
(4)
Post
× Leader born in region
–1.371**
–0.202
–1.243***
–0.850***
(0.546)
(0.322)
(0.368)
(0.315)
× Other regions
–1.370***
–0.406
–0.784**
–0.652**
(0.476)
(0.267)
(0.330)
(0.306)
Observations
159246
159246
159246
159246
Mean dep. var.
4.09
1.21
1.75
0.97
Baseline FEs
✓
✓
✓
✓
Note: The table presents the estimation of the effect of political leaders’ influence on the incidence of conflict following
a Pope’s speech. The unit of observation is a cell × week-year dyad. The sample includes 100 events, defined as papal
peace-seeking speeches targeting a given African country outside of papal trips to Africa, and observations are restricted
to cells where Christian places of worship are recorded. Each event window spans from 5 weeks before to 8 weeks after
the Pope’s speech. The dependent variable equals 100 if at least one conflict event occurs in the cell during the week: any
conflict (col. 1), battle (col. 2), protest/riot (col. 3), or religion-related conflict (col. 4), and 0 otherwise. Post × Leader born
in region is the effect of the speech in cells located in the region where the political leader was born. Post × Other regions
is the effect of the speech in cells located in the other regions. Baseline FEs encompasses cell, event-window-by-country
([−5; +8] weeks around a speech targeting a given country), and week-of-year fixed effects. Standard errors, clustered
at the cell level, are in parentheses. *** p < 0.01, ** p < 0.05, * p < 0.1.
33


conflict incentives, leading to unexpected escalation (Kalyvas, 2006; Wood, 2003). Finally, groups
seeking to assert their legitimacy or dominance might interpret the Pope’s message as a challenge
to their authority, prompting them to intensify violence as a display of power.
By examining religious affiliation and pre-existing violence levels, we aim to better understand
the variation in armed groups’ responses to papal speeches. We exploit a unique feature of the
conflict events dataset: ACLED provides information on the armed groups involved in each violent
event.50 For each actor involved in a conflict event within an event window surrounding a Pope’s
speech, we establish bilateral links with all other actors present in the same event window and
country. Using this framework, we estimate a bilateral violence incidence regression to assess the
likelihood that two armed groups are influenced by the Pope’s speech. Specifically, we estimate
the following specification:
Con f lictg,h,k,i,s,t = α1Posti,s,t + α2(Posti,s,t × Cg,h,i) + ηg,h,i + ωt + µi,s + ϵg,h,i,s,t
(2)
where Con f lictg,h,k,i,s,t represents the incidence of conflict between the armed groups g and h in
cell k, in country i, during week t, within an event window spanning from 5 weeks before to 8 weeks
after the speech s. Posti,s,t is a dummy equal to 1 for weeks following a Pope’s speech mentioning
country i, and 0 otherwise. Cg,h,i is a characteristic of the pair of armed groups (g, h) in country i that
may either reflect a religious attribute or historical violence between groups g and h. For religious
characteristics, the variable Cg,h,i takes three distinct definitions: (i) if at least one of the two groups
is identified as a religious group; (ii) if at least one of the two groups is identified as a Christian
group; and (iii) if at least one of the two groups is identified as an Islamic group.51 To approximate
the history of violence between the two groups, we compute the number of events between groups
g and h from 1997 up to the year preceding the Pope’s speech.52 We define three dummy variables:
the first equals 1 if there is no history of violence between the two groups, the second equals 1 for
pairs of groups with a history of low-intensity violence (fewer than 10 events), and the third equals
1 for groups engaged in high-intensity conflict (10 or more past events). Crucially, we include
actor-pair fixed effects that account for unobserved heterogeneity in actor-pairs (ηg,h,i), resulting in
our inference being based purely on time-varying monadic or bilateral characteristics, an approach
grounded in the gravity trade literature. As in Equation 1, we include week-by-year fixed effects
(ωt) to account for time-specific shocks that may affect all actor-pairs simultaneously, including
seasonal trends or regional instability and event-window-by-country fixed effects (µi,s) to capture
country-specific dynamics within the event window.
Papal speeches, religious affiliation and conflict dynamics.
We analyze how a group’s religious
affiliation influences the bilateral dynamics of violence following a Pope’s speech (Table 9). On
50Notably, ACLED does not specify the perpetrator or victim, nor does it include information on the directionality of
the violence (e.g., who initiated the conflict).
51Note that we have information on religiosity for 79% overall pairs of armed groups. However, only in 0.07% of pairs
both actors are identified as Islamic, and only 0.01% of pairs where both actors are identified as Christians. Therefore,
we cannot estimate the effects when both groups are religious and when they share the same religion.
52Alternatively, we make use of the number of events divided by the number of years of presence of the actor-pair (see
Table I16 in Online Appendix I.4.)
34


average, bilateral violence decreases by nearly 40% after the speech (col. 1). However, this ef-
fect becomes insignificant when at least one of the two groups is identified as religious (col. 2).
Among pairs where neither group is identified as religious, violence decreases by approximately
41%, showing that the effect of the peace-seeking message extends beyond religiously affiliated
groups.53
Next, we distinguish between Christian and Islamic affiliated groups. When at least one group
is identified as Christian, violence declines further (p-value = 0.124), leading to an overall reduction
of approximately 56%. In contrast, for pairs involving at least one Islamic group, the marginal
effect is positive, resulting in a total effect that is not significantly different from zero (col. 3). These
results suggest that while religious identity matters, the perception of the Pope’s message varies
across religious groups. Similar patterns emerge for battles (cols. 4 to 6), though the effects are more
pronounced. Among pairs without religious affiliation, violence decreases by about 77%. When at
least one group is identified as Christian, the reduction reaches 100%. However, for pairs involving
at least one Islamic group, no significant effect is observed. For low-intensity violence, estimates
remain imprecise, preventing clear conclusions about bilateral violence dynamics (cols. 7 to 9).
The findings are particularly striking when focusing on religious violence. On average, the Pope’s
speech has no effect on bilateral religious violence (col. 10). However, when at least one actor is
identified as religious, violence increases significantly by 120% (col. 11). This surge is primarily
driven by pairs where at least one group is identified as Islamic, with violence more than doubling
(230%). Conversely, for pairs where at least one group is identified as Christian, violence decreases
by 70%. This variation aligns with findings on how religious identities shape conflict dynamics,
documenting that perceived bias or external interventions can exacerbate tensions (Cederman et al.,
2011; Tilly, 2003). Additionally, from an analytical perspective, it is reassuring that no effect is
observed on religious violence among pairs where neither group is identified as religious.
History of violence and dynamic of violence.
In Table 10, we analyze how the history of violence
between two groups shapes their responses to the Pope’s speech. Among groups with no prior his-
tory of violence, we observe a significant reduction in the probability of violence following the
speech (approximately 210%, col. 1).54 This aligns with research showing that external interven-
tions are more effective in shaping conflict outcomes when pre-existing hostilities are minimal or
absent (Blattman, 2022). In contrast, for groups with a history of low-intensity violence, there is no
significant effect. For groups with a history of high-intensity violence, the probability of violence
increases by approximately 30%.55 These results remain consistent in both sign and magnitude
53The total effect for each group is computed by combining the baseline effect and the interaction term, accounting for
the variances and covariances of these coefficients. To assess its magnitude, this effect is expressed as a percentage of
the mean dependent variable. For example, for pairs where at least one actor is identified as religious, the total effect is
obtained by summing the interaction term and the baseline post-treatment effect (Post + Post × Actor identified as Religious
= -0.024), then dividing by the mean violence level (Conflict mean = 0.043).
54We express the estimated effects as percentages of the baseline mean for each subgroup defined by past violence.
For each group, we compute the mean of the dependent variable and divide the estimated coefficient by this mean. For
the group with no history of violence (Conflict mean = 0.011), the effect size is -0.023 / 0.011 = -209%.
55For the High intensity history of violence group (Conflict mean = 16.34), the magnitude is computed as 4.88 / 16.34
= 29.8%.
35


when focusing on battles (col. 2), though no significant differences are observed for low-intensity
events (col. 3). When examining religious violence, the findings diverge slightly: any history of vi-
olence, regardless of intensity, is associated with an approximate 30% increase in the probability of
violence. This suggests that the Pope’s speech impacts conflicts differently based on their history,
potentially intensifying hostilities or prompting strategic actions. These findings support the idea
that entrenched rivalries and grievances can hinder de-escalation efforts and external messaging
(Walter, 1997).
6
Conclusion
We provide the first systematic evaluation of the impact of papal peace-promoting speeches on
conflict dynamics in Africa. While religious leaders’ public messages have historically influenced
social norms, economic outcomes, and political landscapes, their effects on conflict remain under-
explored.
Using a comprehensive dataset covering all papal speeches addressing conflicts in Africa from
1997 to 2022 and granular conflict data, we first show that when the Pope targets a country, the
speech is covered in local media, disseminated by dioceses online, and leads individuals to place
greater importance on religion. Employing high-frequency event studies, we document a signif-
icant reduction in conflict incidence (23%) following these speeches. The effects vary depend-
ing on the Pope’s identity, the religious composition of the affected regions, the history of vi-
olence, the alignment of local religious authorities, and the responses of political leaders and
armed groups. Pope John Paul II and Pope Francis’ speeches significantly reduce overall con-
flict likelihood, whereas Pope Benedict XVI’s speeches have no general effect but correlate with
increased battles and religious violence. A turning point emerges in 2006, following the Regens-
burg speech—a particularly controversial address regarding Islam—after which Benedict XVI’s
speeches are associated with an escalation of violence.
To contextualize these findings, we compare the effects of papal speeches with UN Security
Council resolutions, a formal peacekeeping mechanism. While mentions of UN resolutions in local
media increase following their adoption—mirroring the media impact of papal speeches—we find
no significant effect on conflict dynamics. This contrast suggests that religious institutions influence
conflict through moral authority rather than enforcement mechanisms.
We further explore four key mechanisms underlying these heterogeneous effects. First, the
impact of papal speeches is driven by regions with a Christian presence. Second, local religious
institutions play a pivotal role, with bishops ideologically aligned with the Pope and with greater
experience amplifying the speech’s effectiveness. Third, political leaders act as intermediaries in
conflict de-escalation, as violence declines more sharply in their birthplace regions. Finally, armed
groups respond differently based on religious affiliation and prior conflict history. Speeches reduce
overall violence among groups without prior conflict linkages but increase it among those with
entrenched hostilities. Conflicts–particularly religiously motivated ones–decline when at least one
armed group is Christian but rise significantly when at least one group is Islamic.
36


Table 9: Religious affiliation and armed groups’ responses to papal speeches
Panel A: All and Battles
Dependent variable:
Conflict incidence, by type of events:
All
All
All
Battles
Battles
Battles
(1)
(2)
(3)
(4)
(5)
(6)
Post
–0.017***
–0.018***
–0.018***
–0.012***
–0.012***
–0.012***
(0.006)
(0.006)
(0.006)
(0.004)
(0.004)
(0.004)
Post × Actor identified as Religious
0.018**
0.012**
(0.007)
(0.006)
Post × Actor identified as Islamic
0.032**
0.022**
(0.013)
(0.010)
Post × Actor identified as Christian
–0.006
–0.003
(0.004)
(0.003)
Observations
13221052
13221052
13221052
13221052
13221052
13221052
Mean dep. var.
0.04
0.04
0.04
0.02
0.02
0.02
Panel B: Low intensity and Religious
Dependent variable:
Conflict incidence, by type of events:
Low intensity
Low intensity
Low intensity
Religious
Religious
Religious
(7)
(8)
(9)
(10)
(11)
(12)
Post
–0.003
–0.003
–0.003
–0.001
–0.002
–0.002
(0.002)
(0.002)
(0.002)
(0.003)
(0.003)
(0.003)
Post × Actor identified as Religious
0.000
0.014**
(0.001)
(0.006)
Post × Actor identified as Islamic
0.001
0.025**
(0.001)
(0.011)
Post × Actor identified as Christian
–0.001
–0.006
(0.001)
(0.003)
Observations
13221052
13221052
13221052
13221052
13221052
13221052
Mean dep. var.
0.01
0.01
0.01
0.01
0.01
0.01
Event-window × Country FE
✓
✓
✓
✓
✓
✓
Week-of-year FE
✓
✓
✓
✓
✓
✓
Actor Pair FE
✓
✓
✓
✓
✓
✓
Note: The table presents the estimation of the effect of the religious affiliation of armed groups on the incidence of
different types of conflict following a Pope’s speech. The unit of observation is an actor-pair × week-year dyad. The
sample includes 100 events, defined as papal peace-seeking speeches targeting a given African country outside of papal
trips to Africa. Each event window spans from 5 weeks before to 8 weeks after the Pope’s speech. The dependent
variable equals 100 if at least one conflict event occurs in the cell during the week: any conflict (Panel A, col. 1 to 3),
battle (Panel A, col. 4 to 6), protest/riot (Panel B, col. 7 to 9), or religion-related conflict (Panel B, col. 10 to 12), and
0 otherwise. Post is a binary indicator equal to 1 for weeks after a Pope’s speech. Group identified as Religious, Islamic,
Christian are binary indicators equal to 1 if one of the armed group in the pair is identified as religious, or more precisely
Islamic or christian respectively. The three characteristics are interacted with Post. All specifications include actor-pair,
event-window-by-country ([−5; +8] weeks around a speech targeting a given country), and week-of-year fixed effects.
Standard errors, clustered at the actor-pair level, are in parentheses. *** p < 0.01, ** p < 0.05, * p < 0.1.
37


Table 10: History of violence and armed groups’ responses to papal speeches
Dependent variable:
Conflict incidence, by type of events:
All
Battles
Low intensity
Religious
(1)
(2)
(3)
(4)
Post × No history of violence
–0.023***
–0.013***
–0.002
–0.004
(0.005)
(0.003)
(0.002)
(0.003)
Post × History of violence (low intensity)
–0.017
0.056
–0.049
0.101*
(0.134)
(0.078)
(0.039)
(0.059)
Post × History of violence (high intensity)
4.876***
1.100**
0.045
1.187***
(0.878)
(0.480)
(0.243)
(0.452)
Observations
15782049
15782049
15782049
15782049
Note: The table presents the estimation of the effect of the history of violence between armed groups on the incidence
of different types of conflict following a Pope’s speech. The unit of observation is an actor-pair × week-year dyad.
The sample includes 100 events, defined as papal peace-seeking speeches targeting a given African country outside of
papal trips to Africa. Each event window spans from 5 weeks before to 8 weeks after the Pope’s speech. The dependent
variable equals 100 if at least one conflict event occurs in the cell during the week: any conflict (col. 1), battle (col. 2),
protest/riot (col. 3), or religion-related conflict (col. 4), and 0 otherwise. Post is a binary indicator equal to 1 for weeks
after a Pope’s speech. Three levels of history of violence are defined for each pair of actors: no history of violence, low
intensity of past violence and high intensity of past violence, with past violence defined as the number of conflict events
between both actors. The three levels are interacted with Post. All specifications include actor-pair, event-window-by-
country ([−5; +8] weeks around a speech targeting a given country), and week-of-year fixed effects. Standard errors,
clustered at the actor-pair level, are in parentheses. *** p < 0.01, ** p < 0.05, * p < 0.1.
38


Our study deepens the understanding of how religious messaging shapes conflict outcomes,
highlighting the Catholic Church’s distinct role in influencing peace processes. The framework
we develop can extend to other contexts, including the study of religious interventions in political
stability, economic development, and social cohesion. Future research could examine the long-
term implications of papal rhetoric and its interplay with international and domestic peacekeeping
efforts.
39


References
Acemoglu, D., S. Johnson, and J. A. Robinson (2001). The colonial origins of comparative develop-
ment: An empirical investigation. American Economic Review 91(5), 1369–1401.
Adena, M., R. Enikolopov, M. Petrova, V. Santarosa, and E. Zhuravskaya (2015). Radio and the rise
of the nazis in prewar germany. The Quarterly Journal of Economics 130(4), 1885–1939.
Allport, G. W. (1954). The Nature of Prejudice. Reading, MA: Addison-Wesley.
Anderson, S., S. Benetti, and D. Jaramillo (2025). Religious Violence in Africa.
Armand, A., P. Atwell, and J. F. Gomes (2020). The reach of radio: Ending civil conflict through
rebel demobilization. American Economic Review 110(5), 1395–1429.
Assouad, L. (2020, September). Charismatic Leaders and Nation Building. PSE Working papers
hal-02873520, HAL.
Autesserre, S. (2014). Peaceland: Conflict Resolution and the Everyday Politics of International Interven-
tion. Cambridge University Press.
Barro, R. J. (2004). Nothing is Sacred: Economic Ideas for the New Millennium. Cambridge, MA: MIT
Press.
Bassi, V. and I. Rasul (2017, October). Persuasion: A case study of papal influences on fertility-
related beliefs and behavior. American Economic Journal: Applied Economics 9(4), 250–302.
BBC News (2006). Pope’s speech stirs muslim anger. BBC News.
Becker, S. O., J. Rubin, and L. Woessmann (2024, September). Religion and Growth. Journal of
Economic Literature 62(3), 1094–1142.
Becker, S. O. and L. Woessmann (2009). Was weber wrong? a human capital theory of protestant
economic history. The Quarterly Journal of Economics 124(2), 531–596.
Bentzen, J., A. Pizzigolotto, and L. Sperling (2025). Divine Policy: The Impact of Religion in Gov-
ernment. Technical report, American Economic Journal: Applied Economics.
Bentzen, J. S. and G. Gokmen (2023, March). The power of religion. Journal of Economic Growth 28(1),
45–78.
Berman, N. and M. Couttenier (2015).
External shocks, internal shots: The geography of civil
conflicts. Review of Economics and Statistics 97(4), 758–776.
Berman, N., M. Couttenier, D. Rohner, and M. Thoenig (2017). This mine is mine! how minerals
fuel conflicts in africa. American Economic Review 107(6), 1564–1610.
Berman, N., M. Couttenier, and R. Soubeyran (2021). Fertile ground for conflict. Journal of the
European Economic Association 19(1), 82–127.
Bertrand, M. and A. Schoar (2003). Managing with style: The effect of managers on firm policies.
The Quarterly Journal of Economics 118(4), 1169–1208.
Blattman, C. (2022). Why We Fight: The Roots of War and the Paths to Peace. Viking.
Blattman, C. and E. Miguel (2010). Civil war. Journal of Economic Literature 48(1), 3–57.
40


Brown, A. (2017). The war against pope francis. The Guardian.
Burgess, R., R. Jedwab, E. Miguel, A. Morjaria, and G. Padro i Miquel (2015). The value of democ-
racy: Evidence from road building in kenya. American Economic Review 105(6), 1817–1851.
Burhans, M., J. Bell, D. Burhans, R. Carmichael, D. Cheney, M. Deaton, T. Emge, B. Gerlt, J. Grayson,
J. Herries, H. Keegan, A. Skinner, M. Smith, C. Sousa, and S. Trubetskoy (2016).
Diocesean
boundaries of the catholic church [feature layer]. Scale not given.
Bursztyn, L., G. Egorov, and S. Fiorin (2020, November). From extreme to mainstream: The erosion
of social norms. American Economic Review 110(11), 3522–48.
Cagé, J., A. Dagorret, P. Grosjean, and S. Jha (2023, July).
Heroes and villains: The effects of
heroism on autocratic values and nazi collaboration in france. American Economic Review 113(7),
1888–1932.
Cederman, L.-E., H. Buhaug, and J. K. Rød (2009). Ethno-nationalist dyads and civil war: A gis-
based analysis. Journal of Conflict Resolution 53(4), 496–525.
Cederman, L.-E., N. B. Weidmann, and K. S. Gleditsch (2011). Horizontal inequalities and ethnona-
tionalist civil war: A global comparison. American Political Science Review 105(3), 478–495.
Cervellati, M., E. Esposito, and U. Sunde (2022, October). Epidemic Shocks and Civil Violence:
Evidence from Malaria Outbreaks in Africa. The Review of Economics and Statistics 104(4), 780–
796.
Chambru, C. (2019).
Do the right thing!
leaders, weather shocks and social conflicts in pre-
industrial france. Working Papers 0161, European Historical Economics Society (EHES).
Couttenier, M., J. Marcoux, T. Mayer, and M. Thoenig (2024, September). The Gravity of Violence.
SciencePo Working papers hal-04748012, HAL.
DellaVigna, S., R. Enikolopov, V. Mironova, M. Petrova, and E. Zhuravskaya (2014). Cross-border
media and nationalism: Evidence from serbian radio in croatia. American Economic Journal: Ap-
plied Economics 6(3), 103–132.
DellaVigna, S. and E. La Ferrara (2015). Chapter 19 - economic and social impacts of the media. In
S. P. Anderson, J. Waldfogel, and D. Strömberg (Eds.), Handbook of Media Economics, Volume 1 of
Handbook of Media Economics, pp. 723–768. North-Holland.
Depetris-Chauvin, E., R. Durante, and F. Campante (2020). Building nations through shared expe-
riences: Evidence from african football. American Economic Review 110(5), 1572–1602.
Djourelova, M., R. Durante, and G. J. Martin (2024, 05). The impact of online competition on local
newspapers: Evidence from the introduction of craigslist. The Review of Economic Studies, rdae049.
Dube, O. and J. F. Vargas (2013). Commodity price shocks and civil conflict: Evidence from colom-
bia. Review of Economic Studies 80(4), 1384–1421.
Eberle, U. J., D. Rohner, and M. Thoenig (2020). Heat and hate: Climate security and farmer-herder
conflicts in africa.
Ellis, S. and G. ter Haar (1998). Religion and politics in sub-saharan africa. The Journal of Modern
African Studies 36(2), 175–201.
41


Engelberg, J., R. Fisman, J. C. Hartzell, and C. A. Parsons (2016). Human capital and the supply of
religion. Review of Economics and Statistics 98(3), 415–427.
Esposito, E., T. Rotesi, A. Saia, and M. Thoenig (2023). Reconciliation narratives: The birth of a
nation after the us civil war. American Economic Review 113(6), 1461–1504.
Esteban, J., L. Mayoral, and D. Ray (2012). Ethnicity and conflict: An empirical study. American
Economic Review 102(4), 1310–1342.
Fearon, J. D. (1995). Rationalist explanations for war. International Organization 49(3), 379–414.
Fearon, J. D. and D. D. Laitin (2004). Neotrusteeship and the problem of weak states. International
Security 28(4), 5–43.
Fraga, B. (2023). For 10 years, pope francis outlasts the conservative resistance. National Catholic
Reporter.
Francis, P. (2013). Evangelii Gaudium (The Joy of the Gospel). Vatican City: Vatican Publishing House.
Franck, R. and I. Rainer (2012). Does the leader’s ethnicity matter? ethnic favoritism, education,
and health in sub-saharan africa. American Political Science Review 106(2), 294–325.
Freston, P. (2001). Evangelicals and Politics in Asia, Africa and Latin America. Cambridge University
Press.
Gagliarducci, S., M. G. Onorato, F. Sobbrio, and G. Tabellini (2020). War of the waves: Radio and
resistance during world war ii. American Economic Journal: Applied Economics 12(4), 246–276.
Galtung, J. (1969). Violence, peace, and peace research. Journal of Peace Research 6(3), 167–191.
Glaeser, E. L. and C. R. Sunstein (2009). Extremism and social learning. Journal of Legal Analysis 1(1),
263–324.
Grosjean, P., F. Masera, and H. Yousaf (2023, 09). Inflammatory political campaigns and racial bias
in policing*. The Quarterly Journal of Economics 138(1), 413–463.
Guarnieri, E. (2025). Cultural Distance and Ethnic Civil Conflict.
Guarnieri, E. and A. Tur-Prats (2023, August). Cultural Distance and Conflict-Related Sexual Vio-
lence. The Quarterly Journal of Economics 138(3).
Harari, M. and E. L. Ferrara (2018). Conflict, climate, and cells: a disaggregated analysis. Review of
Economics and Statistics 100(4), 594–608.
Hastings, A. (1994). The Church in Africa, 1450–1950. Oxford: Oxford University Press.
Hatte, S., J. Loper, and T. Taylor (2025). Connecting the unconnected: Facebook access and female
political representation in sub-saharan africa. Available at SSRN 5176903.
Hatte, S., E. Madinier, and E. Zhuravskaya (2021). Reading twitter in the newsroom: Web 2.0 and
traditional-media reporting of conflicts. CEPR Discussion Paper No. DP16167.
Hodler, R. and P. A. Raschky (2014). Regional favoritism. The Quarterly Journal of Economics 129(2),
995–1033.
Hutchinson, S. E. (1996). Nuer Dilemmas: Coping with Money, War, and the State in Southern Sudan.
Berkeley, CA: University of California Press.
42


Iannaccone, L. R. (1998).
Introduction to the economics of religion.
Journal of Economic Litera-
ture 36(3), 1465–1495.
Ivereigh, A. (2014). The Great Reformer: Francis and the Making of a Radical Pope. New York: Henry
Holt and Company.
Iyer, S. (2016, June). The New Economics of Religion. Journal of Economic Literature 54(2), 395–441.
Iyigun, M., N. Nunn, and N. Qian (2017, November). The Long-run Effects of Agricultural Pro-
ductivity on Conflict, 1400-1900. NBER Working Papers 24066, National Bureau of Economic
Research, Inc.
Jervis, R. (1976). Perception and Misperception in International Politics. Princeton University Press.
John Paul II (1983). Code of Canon Law. Vatican.
John Paul II (1995). Ut Unum Sint (On Commitment to Ecumenism). Vatican City: Libreria Editrice
Vaticana. Encyclical Letter.
John Paul II, P. (1994). Ecclesia in africa: Post-synodal apostolic exhortation on the church in africa
and its evangelizing mission towards the year 2000.
Johnson, D. H. (2011). The Root Causes of Sudan’s Civil Wars: Peace or Truce? Oxford: James Currey.
Jones, B. F. and B. A. Olken (2005, 08). Do leaders matter? national leadership and growth since
world war ii*. The Quarterly Journal of Economics 120(3), 835–864.
Jones, B. F. and B. A. Olken (2009, July). Hit or miss? the effect of assassinations on institutions and
war. American Economic Journal: Macroeconomics 1(2), 55–87.
Kalyvas, S. N. (2006). The Logic of Violence in Civil War. Cambridge University Press.
Lamb, C. (2020). The Outsider: Pope Francis and His Battle to Reform the Church. Maryknoll, NY: Orbis
Books.
Laville, C. (2021). Religious authorities, peace, and political conflict: Assessing the impacts of pope
john paul ii’s international travels. Working Papers hal-03137434, HAL.
Marshall, B. D. (2012). Benedict xvi as theologian and pope. Theological Studies 73(3), 512–538.
Martinez-Bravo, M., D. Solá, and G. Tuñon (2025). The Catholic Church and Redistributive Conflict:
The Effects of John Paul II’s Rollback of Progressivism in Brazil.
McCleary, R. M. and R. J. Barro (2006). Religion and economy. Journal of Economic Perspectives 20(2),
49–72.
McGuirk, E. and M. Burke (2020). The economic origins of conflict in africa. Journal of Political
Economy 128(10), 3940–3997.
McGuirk, E. and M. Burke (2022). War in ukraine, world food prices, and conflict in africa. In
L. Garicano, D. Rohner, and B. Weder di Mauro (Eds.), Global Economic Consequences of the War in
Ukraine: Sanctions, Supply Chains and Sustainability. London and Paris: CEPR Press.
McGuirk, E. F. and N. Nunn (2024). Development mismatch? evidence from agricultural projects
in pastoral africa. Technical report, National Bureau of Economic Research.
43


McGuirk, E. F. and N. Nunn (2025). Transhumant pastoralism, climate change, and conflict in
africa. Review of Economic Studies 92(1), 404–441.
McNeil, D. G. (2009, March). Pope’s comments on condoms set off international criticism. The New
York Times.
Michalopoulos, S. and E. Papaioannou (2016, July). The long-run effects of the scramble for africa.
American Economic Review 106(7), 1802–48.
Miguel, E., S. Satyanath, and E. Sergenti (2004). Economic shocks and civil conflict: An instrumental
variables approach. Journal of Political Economy 112(4), 725–753.
Mougin, E. (2024). Tv in times of political uncertainty: Evidence from the 2017 elections in kenya.
Journal of Development Economics 166, 103179.
Muller, K. and C. Schwarz (2023, July). From hashtag to hate crime: Twitter and antiminority
sentiment. American Economic Journal: Applied Economics 15(3), 270–312.
O’Connell, G. (2019). The Election of Pope Francis: An Inside Account of the Conclave That Changed
History. Maryknoll, NY: Orbis Books.
O’Malley, J. W. (2008). What Happened at Vatican II. Cambridge, MA: Harvard University Press.
Orobator, A. E. (2018). Religion and Faith in Africa: Confessions of an Animist. Maryknoll, NY: Orbis
Books.
Pearlman, W. (2013). Emotions and the microfoundations of the arab uprisings. Perspectives on
Politics 11(2), 387–409.
Petersen, R. D. (2002).
Understanding Ethnic Violence: Fear, Hatred, and Resentment in Twentieth-
Century Eastern Europe. Cambridge University Press.
Pew Research Center (2010). Tolerance and tension: Islam and christianity in sub-saharan africa.
Powell, R. (2006). War as a commitment problem. International Organization 60(1), 169–203.
Pruitt, D. G. and S. H. Kim (2004). Social Conflict: Escalation, Stalemate, and Settlement. McGraw-Hill.
Prunier, G. (1997). The Rwanda Crisis: History of a Genocide. New York: Columbia University Press.
Raleigh, C., R. Linke, H. Hegre, and J. Karlsen (2010). Introducing acled: An armed conflict location
and event dataset. Journal of peace research 47(5), 651–660.
Rohner, D. (2024a). Mediation, Military, and Money: The Promises and Pitfalls of Outside Inter-
ventions to End Armed Conflicts. Journal of Economic Literature 62(1), 155–195.
Rohner, D. (2024b). The Peace Formula: Voice, Work and Warranties, Not Violence. Cambridge: Cam-
bridge University Press.
Rohner, D. and E. Zhuravskaya (Eds.) (2023). Nation Building: Big Lessons from Successes and Failures.
Paris and London: CEPR Press.
Rowland, T. (2008). Ratzinger’s Faith: The Theology of Pope Benedict XVI. Oxford: Oxford University
Press.
Sawyer, A. (2004). Violent conflicts and governance challenges in west africa: The case of the mano
river basin area. Journal of Modern African Studies 42(3), 437–463.
44


Second Vatican Council (1965). Decree christus dominus: On the pastoral office of bishops in the
church. Section 20.
Seewald, P. (2020). Benedict XVI: A Life. London: Bloomsbury Continuum.
Seyranian, V. (2014). Social identity framing communication strategies for mobilizing social change.
The Leadership Quarterly 25(3), 468–486.
Seyranian, V. and M. C. Bligh (2008). Presidential charismatic leadership: Exploring the rhetoric of
social change. The Leadership Quarterly 19(1), 54–76.
Tarrow, S. (2005). The New Transnational Activism. Cambridge, UK: Cambridge University Press.
Thornton, J. F. and S. B. Varenne (Eds.) (2008). The Essential Pope Benedict XVI: His Central Writings
and Speeches. New York: HarperOne.
Tilly, C. (2003). The Politics of Collective Violence. Cambridge University Press.
Turner, T. (2007). The Congo Wars: Conflict, Myth, and Reality. London: Zed Books.
Vatican Press (1917). 1917 Code of Canon Law. Vatican City: Vatican Press. Also known as the
Pio-Benedictine Code.
Walter, B. F. (1997). The critical barrier to civil war settlement. International Organization 51(3),
335–364.
Walter, B. F. (2014). Why bad governance leads to repeat civil war. Journal of Conflict Resolution 58(2),
306–336.
Wang, T. (2021, September). Media, pulpit, and populist persuasion: Evidence from father cough-
lin. American Economic Review 111(9), 3064–92.
Weigel, G. (1999). Witness to Hope: The Biography of Pope John Paul II. New York: HarperCollins.
Weinstein, J. M. (2007). Inside Rebellion: The Politics of Insurgent Violence. Cambridge University
Press.
Wood, E. J. (2003). Insurgent Collective Action and Civil War in El Salvador. Cambridge University
Press.
Yanagizawa-Drott, D. (2014). Propaganda and conflict: Evidence from the rwandan genocide. The
Quarterly Journal of Economics 129(4), 1947–1994.
45


CENTRE FOR ECONOMIC PERFORMANCE 
Recent Discussion Papers 
 
2093 
Melanie Arntz 
Michael J. Böhm 
Georg Graetz 
Terry Gregory 
Florian Lehmer 
Cäcilia Lipowski 
Firm-level technology adoption in times of 
crisis 
2092 
Janine Boshoff 
Stephen Machin 
Matteo Sandi 
Youth crime and delinquency in and out of 
school 
2091 
Philippe Aghion 
Antonin Bergeaud 
Mathias Dewatripont 
Johannes Matt 
Firm dynamics and growth with soft budget 
constraints 
2090 
Kristen B. Cooper 
Ori Heffetz 
John Ifcher 
Ekaterina Oparina 
Stephen Wu 
Teaching happiness (economics) in your 
dismal-science courses 
2089 
Andrew Mountford 
Jonathan Wadsworth 
Immigration, demand, supply and sectoral 
heterogeneity in the UK labour market 
2088 
Andrés Rodríguez-Clare 
Mauricio Ulate 
Jose P. Vasquez 
Trade with nominal rigidities: Understanding 
the unemployment and welfare effects of the 
China shock 
2087 
Anthony J. Venables 
Location choice when the number of jobs 
matters: Matching in spatial equilibrium 
2086 
Philippe Aghion 
Timo Boppart 
Michael Peters 
Matthew Schwartzman 
Fabrizio Zilibotti 
A theory of endogenous degrowth and 
environmental sustainability 


2085 
Christos Genakos 
Mario Pagliero 
Lorien Sabatino 
Tommaso Valletti 
Cultural exception? The impact of price 
regulation on prices and variety in the market 
for books 
2084 
Paolo Conconi 
Fabrizio Leone 
Glenn Magerman 
Catherine Thomas 
Multinational networks and trade participation 
2083 
Anna Gumpert 
Kalina Manova 
Cristina Rujan 
Monika Schnitzer 
Multinational firms and global innovation 
2082 
Kalina Manova 
Andreas Moxnes 
Oscar Perelló 
Productivity, matchability and intermediation 
in production networks 
2081 
Hélène Donnat 
Luz Yadira Gómez-Hernández 
Nicolás González-Pampillón 
Gonzalo Nunez-Chaim 
Henry G. Overman 
Evaluating the local economic impacts of 
transport projects and programmes (with an 
application to UK Local Major schemes) 
2080 
Stephen J. Redding 
Evaluating transport improvements in spatial 
equilibrium 
2079 
Tito Boeri 
Tommaso Crescioli 
Andrea Garnero 
Lorenzo G. Luisetto 
Collective bargaining and monopsony: The 
regulation of noncompete agreements in 
France 
2078 
Mauricio Ulate 
Jose P. Vsquez 
Roman D. Zarate 
Labour market effects of global supply chain 
disruptions 
The Centre for Economic Performance Publications Unit 
Tel: +44 (0)20 7955 7673 Email info@cep.lse.ac.uk 
Website: http://cep.lse.ac.uk Twitter: @CEP_LSE 
