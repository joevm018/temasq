# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ConsentFacial(models.Model):
    _name = 'consent.facial'

    update_date = fields.Date('Facial Date', default=fields.Date.context_today, required=True)
    type = fields.Selection([('facial', 'FACIAL'),
                             ('hair_spa', 'HAIR SPA'),
                             ('hair_color', 'HAIR COLOR'),
                             ('hair_treatment', 'HAIR TREATMENT'),
                             ('hammam', 'HAMMAM'),
                             ('massage', 'MASSAGE'),
                             ('customer_tips', 'CUSTOMER TIPS'),
                             ('lashes', 'LASHES')], "Type")
    customer_id = fields.Many2one('res.partner', 'Customer', required=True)
    survey = fields.Selection([('word', 'Word of mouth'),
                               ('Social Media', 'Social Media'),
                               ('walkby', 'Walk by'),
                               ('website', 'Our Website')], "How did you hear about us?")
    customer_signature = fields.Binary(string='Customer Signature')
    salon_signature = fields.Binary(string='Administrative Signature')

    f1 = fields.Char("1 -What is your main goal for today treatment ?")
    f2 = fields.Char("2-What is your skin care routine?")
    f3 = fields.Char("3 -what skin care products are you using?")
    f4 = fields.Char("4 -Are you Wearing Eyelashes?")
    f5 = fields.Selection([('yes', 'Yes نعم'),
                           ('no', 'No لا')], 'Have you Ever your skin care had a facial before?')
    f51 = fields.Char("Notes")
    f6 = fields.Selection([('yes', 'Yes نعم'),
                           ('no', 'No لا')], 'Do you have any special skin problems?')
    f61 = fields.Char("Notes")
    f7 = fields.Selection([('yes', 'Yes نعم'),
                           ('no', 'No لا')], 'Have you ever take any chemical peels?')
    f71 = fields.Char("Notes")
    f8 = fields.Selection([('yes', 'Yes نعم'),
                           ('no', 'No لا')], 'Have you even used an acne medicine?')
    f81 = fields.Char("Notes")
    f9 = fields.Selection([('break', 'Break out/Ache'),
                           ('black', 'Black/white Heads'),
                           ('dry', 'Dryness'),
                           ('relax', 'Relaxations')], 'What concern do you have regarding your skin?')
    f10 = fields.Boolean('Sensitivity')
    f11 = fields.Boolean('Eczema')
    f12 = fields.Boolean('Pigmentations')
    f13 = fields.Boolean('Melasma')
    f14 = fields.Boolean('Flabby Face')
    f15 = fields.Boolean('Burns')
    f16 = fields.Boolean('Pregnant')
    f17 = fields.Boolean('Acne')
    f18 = fields.Selection([
        ('Normal', 'Normalعادية'),
        ('Oily', 'Oily دهنية'),
        ('Dry', 'Dryجافة'),
        ('Mixed', 'Mixedمختلطة'),
        ('VeryDry', 'Very dryجافة جدا'),
        ('DrySensitive', 'Dry and sensitiveجافة و حساسة')], 'Skin typeنوع البشرة')
    f19 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], string="Have you cleaned the skin?هل قمت بتنظيف البشرة؟")
    f20 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Have you peeling the skin?هل قمت بتقشير البشرة؟')
    f21 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')],
                           'Did you use sweetness, wax, or floss for the face? هل قمت باستخدام الحلاوة, الشمع او الخيط للوجه؟')
    f22 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Have you used face laser? هل قمت باستخدام الليزر للوجه؟')
    f23 = fields.Text("Treatment stages and steps مراحل العلاج و الخطوات")
    f24 = fields.Selection([('1session', '1 sessionجلسة واحدة'),
                            ('3session', '3 sessions3 جلسات'),
                            ('4session', '4 sessions4 جلسات'),
                            ('6session', '6 sessions5 جلسات')], 'Number of sessionsعدد الجلسات المقررة')
    f34 = fields.Char("Notes:ملاحظات: ")

    s1 = fields.Boolean("Allergies")
    s2 = fields.Boolean("Pregnant")
    s3 = fields.Boolean("Contact lenses")
    s4 = fields.Boolean("Breast Feeding")
    s5 = fields.Boolean("Heat Sensitivity")
    s6 = fields.Boolean("Normal")
    s7 = fields.Boolean("Oily")
    s8 = fields.Boolean("Dry / Sensitive")
    s9 = fields.Boolean("Dandruff")
    s10 = fields.Boolean("Normal")
    s11 = fields.Boolean("Dry")
    s12 = fields.Boolean("Damage / Illastic")
    s13 = fields.Boolean("Oily")
    s14 = fields.Boolean("Frizzy")
    s15 = fields.Boolean("Dull")
    s16 = fields.Boolean("Falling Hair")
    s17 = fields.Boolean("Split Ends")
    s18 = fields.Boolean("Chemically Threat")
    s19 = fields.Boolean("Colored")
    s20 = fields.Boolean("Straight")
    s21 = fields.Boolean("Wavy")
    s22 = fields.Boolean("Curly")
    s23 = fields.Boolean("Kinky")
    s24 = fields.Boolean("African Hair")
    s25 = fields.Boolean("Eczema")
    s26 = fields.Boolean("Hair Loss")
    s27 = fields.Boolean("Dandruff")
    s28 = fields.Boolean("Henna")
    s29 = fields.Boolean("Gaps in the hair")
    s30 = fields.Boolean("Highlight or Hair Color")
    s31 = fields.Boolean("Sensitivity towards color")
    s32 = fields.Boolean("White hair")

    s38 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '1- Have you had any brain / head / neck / shoulder Surgery?')
    s39 = fields.Char("When")
    s44 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '4- • When was the last time you had any chemical treatment?')
    s45 = fields.Char("When")
    s46 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '5- Are you under any kind of food region?')
    s47 = fields.Char("Type")
    s48 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '6- • Have you lost weight in past few months?')
    s49 = fields.Char("Type")
    s50 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')],
                           '7- • Are you using any kind of house hair remedies / vitamins / supplement at home?')
    s51 = fields.Char("Type")
    s52 = fields.Char("8-  • Please list any physical or health conditions that your therapist should be aware")
    s53 = fields.Char(
        "9- • Please list any medication taken regularly and any specific medication / pain killer taken today?")
    s54 = fields.Char("10- •What would you like to gain from your treatment today?")
    s55 = fields.Char("11- •Please list any physical or health conditions that your therapist should be aware")
    s56 = fields.Char("12- • RECOMMENDED TREATMENT:")
    s57 = fields.Char("13- • APPLICATION:")
    s58 = fields.Char("14- • Notes:")
    s59 = fields.Integer("No of Session")
    s60 = fields.Char("Duration")
    s61 = fields.Char("Therapist")
    s62 = fields.Char("Staff Name")
    s63 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'Stay Rooted ستاي روتد')
    s64 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'Quench my thirst كوينش ماي ثيرست')
    s65 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'Scalp therapy سكالب ثيرابي')
    s66 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'Watch me grow واتش مي غرو')
    s67 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'Aloe Vera ألوفيرا')
    s68 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'Survivor سورفايفر')
    s69 = fields.Selection([('word', 'Word of mouth'),
                            ('media', 'Social Media'),
                            ('walkby', 'Walk by'),
                            ('website', 'Our Website')], "How did you hear about us?")
    s70 = fields.Binary(string='Customer Signature')
    s71 = fields.Binary(string='Administrative Signature')

    c1 = fields.Boolean("Allergies")
    c2 = fields.Boolean("Pregnant")
    c3 = fields.Boolean("Contact lenses")
    c4 = fields.Boolean("Breast Feeding")
    c5 = fields.Boolean("Heat Sensitivity")
    c6 = fields.Boolean("Normal")
    c7 = fields.Boolean("Oily")
    c8 = fields.Boolean("Dry / Sensitive")
    c9 = fields.Boolean("Dandruff")
    c10 = fields.Boolean("Normal")
    c11 = fields.Boolean("Dry")
    c12 = fields.Boolean("Damage / Illastic")
    c13 = fields.Boolean("Oily")
    c14 = fields.Boolean("Frizzy")
    c15 = fields.Boolean("Dull")
    c16 = fields.Boolean("Falling Hair")
    c17 = fields.Boolean("Split Ends")
    c18 = fields.Boolean("Chemically Threat")
    c19 = fields.Boolean("Colored")
    c20 = fields.Boolean("Straight")
    c21 = fields.Boolean("Wavy")
    c22 = fields.Boolean("Curly")
    c23 = fields.Boolean("Kinky")
    c24 = fields.Boolean("African Hair")
    c25 = fields.Boolean("Eczema")
    c26 = fields.Boolean("Hair Loss")
    c27 = fields.Boolean("Dandruff")
    c28 = fields.Boolean("Henna")
    c29 = fields.Boolean("Gaps in the hair")
    c30 = fields.Boolean("Highlight or Hair Color")
    c31 = fields.Boolean("Sensitivity towards color")
    c32 = fields.Boolean("White hair")
    c33 = fields.Boolean("New Growth")
    c34 = fields.Boolean("Color")
    c35 = fields.Boolean("Ransage")
    c36 = fields.Boolean("Baylage")
    c37 = fields.Boolean("High light / Ombrey")
    c371 = fields.Boolean("Root color")
    c372 = fields.Boolean("Full hair color")
    c373 = fields.Boolean("Sombre")
    c374= fields.Boolean("ombrey")
    c375 = fields.Boolean("Bleach")
    c376 = fields.Boolean("henna")
    c38 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '1- Have you had any brain / head / neck / shoulder Surgery?')
    c39 = fields.Char("When")
    c40 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '2- • When was the last time you colored your hair?')
    c41 = fields.Char("When")
    c42 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '3- • When was the last time you did fulled color?')
    c43 = fields.Char("When")
    c44 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '4- • When was the last time you had any chemical treatment?')
    c45 = fields.Char("When")
    c46 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '5- Are you under any kind of food region?')
    c47 = fields.Char("Type")
    c48 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '6- • Have you lost weight in past few months?')
    c49 = fields.Char("Type")
    c50 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')],
                           '7- • Are you using any kind of house hair remedies / vitamins / supplement at home?')
    c51 = fields.Char("Type")
    c52 = fields.Char("8-  • Please list any physical or health conditions that your therapist should be aware")
    c53 = fields.Char(
        "9- • Please list any medication taken regularly and any specific medication / pain killer taken today?")
    c54 = fields.Char("10- •What would you like to gain from your treatment today?")
    c55 = fields.Char("11- •Please list any physical or health conditions that your therapist should be aware")
    c56 = fields.Char("12- • RECOMMENDED TREATMENT:")
    c57 = fields.Char("13- • APPLICATION:")
    c58 = fields.Char("14- • Notes ملاحظات الموظفة:")
    c59 = fields.Integer("No of Session")
    c60 = fields.Char("Duration")
    c61 = fields.Char("Therapist")
    c62 = fields.Char("Staff Name")
    c63 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Root color صبغة جذور')
    c64 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Full hair color صبغة كاملة')
    c65 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'High light هاي لايت')
    c66 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Low light (balayage) لو لايت (بالياج)')
    c67 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Rinsage رانساج')
    c68 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'sombre سومبريه')
    c681 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'ombre أومبريه')
    c682 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Protection حماية للشعر')
    c69 = fields.Selection([('word', 'Word of mouth'),
                            ('media', 'Social Media'),
                            ('walkby', 'Walk by'),
                            ('website', 'Our Website')], "How did you hear about us?")
    c70 = fields.Binary(string='Customer Signature')
    c71 = fields.Binary(string='Administrative Signature')

    t1 = fields.Boolean("Allergies")
    t2 = fields.Boolean("Pregnant")
    t3 = fields.Boolean("Contact lenses")
    t4 = fields.Boolean("Breast Feeding")
    t5 = fields.Boolean("Heat Sensitivity")
    t6 = fields.Boolean("Normal")
    t7 = fields.Boolean("Oily")
    t8 = fields.Boolean("Dry / Sensitive")
    t9 = fields.Boolean("Dandruff")
    t10 = fields.Boolean("Normal")
    t11 = fields.Boolean("Dry")
    t12 = fields.Boolean("Damage / Illastic")
    t13 = fields.Boolean("Oily")
    t14 = fields.Boolean("Frizzy")
    t15 = fields.Boolean("Dull")
    t16 = fields.Boolean("Falling Hair")
    t17 = fields.Boolean("Split Ends")
    t18 = fields.Boolean("Chemically Threat")
    t19 = fields.Boolean("Colored")
    t20 = fields.Boolean("Straight")
    t21 = fields.Boolean("Wavy")
    t22 = fields.Boolean("Curly")
    t23 = fields.Boolean("Kinky")
    t24 = fields.Boolean("African Hair")
    t25 = fields.Boolean("Eczema")
    t26 = fields.Boolean("Hair Loss")
    t27 = fields.Boolean("Dandruff")
    t28 = fields.Boolean("Henna")
    t29 = fields.Boolean("Gaps in the hair")
    t30 = fields.Boolean("Highlight or Hair Color")
    t31 = fields.Boolean("Sensitivity towards color")
    t32 = fields.Boolean("White hair")

    t38 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '1- Have you had any brain / head / neck / shoulder Surgery?')
    t39 = fields.Char("When")
    t44 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '4- • When was the last time you had any chemical treatment?')
    t45 = fields.Char("When")
    t46 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '5- Are you under any kind of food region?')
    t47 = fields.Char("Type")
    t48 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], '6- • Have you lost weight in past few months?')
    t49 = fields.Char("Type")
    t50 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')],
                           '7- • Are you using any kind of house hair remedies / vitamins / supplement at home?')
    t51 = fields.Char("Type")
    t52 = fields.Char("8-  • Please list any physical or health conditions that your therapist should be aware")
    t53 = fields.Char(
        "9- • Please list any medication taken regularly and any specific medication / pain killer taken today?")
    t54 = fields.Char("10- •What would you like to gain from your treatment today?")
    t55 = fields.Char("11- •Please list any physical or health conditions that your therapist should be aware")
    t56 = fields.Char("12- • RECOMMENDED TREATMENT:")
    t57 = fields.Char("13- • APPLICATION:")
    t58 = fields.Char("14- • Notes:")
    t59 = fields.Integer("No of Session")
    t60 = fields.Char("Duration")
    t61 = fields.Char("Therapist")
    t62 = fields.Char("Staff Name")
    t63 = fields.Selection([('30', '30%-50%'),
                            ('60', '60%-70%')],
                           'S Squared straightening')
    t69 = fields.Selection([('word', 'Word of mouth'),
                            ('media', 'Social Media'),
                            ('walkby', 'Walk by'),
                            ('website', 'Our Website')], "How did you hear about us?")
    t70 = fields.Binary(string='Customer Signature')
    t71 = fields.Binary(string='Administrative Signature')

    h1 = fields.Boolean("Repetitive Injury")
    h2 = fields.Boolean("Numbness")
    h3 = fields.Boolean("Pain/Swelling")
    h4 = fields.Boolean("Inflammation")
    h5 = fields.Boolean("Cold/Flu/Virus")
    h6 = fields.Boolean("Chest|Breathing")
    h7 = fields.Boolean("Headaches \ Dizziness")
    h8 = fields.Boolean("Sleeping Problems")
    h9 = fields.Boolean("Depression|Anxiety")
    h10 = fields.Boolean("Surgery")
    h11 = fields.Boolean("Heart Problem")
    h12 = fields.Boolean("High/Low Blood Pressure")
    h13 = fields.Boolean("Digestive Problem")
    h14 = fields.Boolean("Diabetes or Epilepsy")
    h15 = fields.Boolean("Cancer")
    h16 = fields.Boolean("Blood Clots")
    h17 = fields.Boolean("Thrombosis")
    h18 = fields.Boolean("Allergies")
    h19 = fields.Boolean("Contact Lenses")
    h20 = fields.Boolean("Skin Sensitivity")
    h21 = fields.Boolean("Pregnant/Breast Feeding")
    h22 = fields.Boolean("Post Natal/Pre Menstrual")
    h23 = fields.Boolean("Menopausal")
    h24 = fields.Boolean("Botox/Dermal Fillers")
    h25 = fields.Boolean("Chemical Peels")
    h26 = fields.Boolean("Heat Sensitivity")
    h27 = fields.Boolean("Claustrophobia")
    h29 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], "Wax?")
    h30 = fields.Char("when is the last time?")
    h31 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], "Laser")
    h32 = fields.Char("when is the last time?")

    h52 = fields.Char("1- • Please list any physical or health conditions that your therapist should be aware Of")
    h53 = fields.Char(
        "2- • Please list any medication taken regularly and any specific medication/pain killers taken today")
    h54 = fields.Char("3- • What would you like to gain from your treatment today?")
    h55 = fields.Char("4- • When was the last time you had facial/wax/hammam/face bleaching?")
    h56 = fields.Char("5- • How many glasses of water ____caffeinated drinks ____do you drinking a day?")
    h57 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Pregnant حامل')
    h58 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Surgery عملية جراحية')
    h59 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'High blood pressure ضغط دم مرتفع')
    h60 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Skin allergy حساسية جلد')
    h61 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Eczema أكزيما')
    h62 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Asthma ربو')
    h63 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Feller فيلر في الوجه')
    h64 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Other غيره')
    h65 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'WHITENING حمام التبيض')
    h66 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'Moroccan bath الحمام المغربي')
    h67 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'Samia’s favorite bath حمام سامية المفضل')
    h68 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'Samia’s signature bath حمام سامية الخاص')
    h681 = fields.Selection([('session', 'ONE SESSION جلسة واحدة'),
                            ('package', 'PACKAGE باكج')],
                           'Other غيره')
    h682 = fields.Char("14- • Notes:")
    h69 = fields.Selection([('word', 'Word of mouth'),
                            ('media', 'Social Media'),
                            ('walkby', 'Walk by'),
                            ('website', 'Our Website')], "How did you hear about us?")
    h70 = fields.Binary(string='Customer Signature')
    h71 = fields.Binary(string='Administrative Signature')

    m1 = fields.Boolean("Repetitive Injury")
    m2 = fields.Boolean("Numbness")
    m3 = fields.Boolean("Pain/Swelling")
    m4 = fields.Boolean("Inflammation")
    m41 = fields.Boolean("Joint problem الام المفاصل")
    m42 = fields.Boolean("Muscular problem مشاكل عضلية")
    m5 = fields.Boolean("Cold/Flu/Virus")
    m6 = fields.Boolean("Chest|Breathing")
    m7 = fields.Boolean("Headaches \ Dizziness")
    m8 = fields.Boolean("Sleeping Problems")
    m9 = fields.Boolean("Depression|Anxiety")
    m10 = fields.Boolean("Surgery جراحة")
    m11 = fields.Boolean("Heart Problem مشاكل القلب")
    m12 = fields.Boolean("High/ Low blood pressure انخفاض ظغط الدم وارتفاعه")
    m13 = fields.Boolean("Digestive Problem")
    m14 = fields.Boolean("Diabetes or Epilepsy السكري او الصرع")
    m15 = fields.Boolean("Cancer")
    m16 = fields.Boolean("Blood Clots")
    m17 = fields.Boolean("Thrombosis")
    m18 = fields.Boolean("Allergies")
    m19 = fields.Boolean("Contact Lenses")
    m20 = fields.Boolean("Skin Sensitivity")
    m21 = fields.Boolean("Pregnant/Breast Feeding")
    m22 = fields.Boolean("Post Natal/Pre Menstrual")
    m23 = fields.Boolean("Menopausal")
    m24 = fields.Boolean("Botox/Dermal Fillers")
    m25 = fields.Boolean("Chemical Peels")
    m26 = fields.Boolean("Heat Sensitivity")
    m27 = fields.Boolean("Claustrophobia")

    m271 = fields.Boolean("mom wellness")
    m272 = fields.Boolean("polynisia")
    m273 = fields.Boolean("indosian")
    m274 = fields.Boolean("body wrapping")
    m275 = fields.Boolean("marine care")

    m28 = fields.Boolean("Desk/Computer Work")
    m29 = fields.Boolean("Physical Activities")
    m30 = fields.Boolean("Travel")

    m31 = fields.Boolean("SA BODY SPA")
    m32 = fields.Boolean("SA BODY MASSAGE")
    m321 = fields.Boolean("SAMIA”S FAVORITE BODY MASSAGE مساج سامية المفضل")
    m322 = fields.Boolean("MUMS WELLNESS")
    m323 = fields.Boolean("DEEP TISSUES MASSAGE مساج الألام العضلية")
    m324 = fields.Boolean("BODY MASSAGE AROMA THERAPY CANDLE WAX MASSAGE مساج الزيوت العطرية")
    m325 = fields.Boolean("HERBAL THAI MASSAGE")
    m326 = fields.Boolean("HOT STONE MASSAGE")
    m327 = fields.Boolean("NECK, SHOULDERS, HEAD MASSAGE مساج  الرأس,الكتف,الرقبة")

    m33 = fields.Boolean("Full Body")
    m34= fields.Boolean("Upper Body")
    m35 = fields.Boolean("Hands & Feet")
    m36 = fields.Boolean("Scalp/Sinus")

    m37 = fields.Selection([('light', 'Light'),
                            ('medium', 'Medium'),
                            ('firm', 'Firm'),
                            ('deep', 'Deep'),
                            ('trigger', 'With Trigger Points')], 'Pressure')
    m38 = fields.Selection([('Normal', 'Normal'),
                            ('sensistive', 'Sensitive'),
                            ('dry', 'Dry')], 'Skin')
    m381 = fields.Selection([('COLD', 'COLD'),
                            ('WARM', 'WARM'),
                            ('NORMAL', 'NORMAL')], 'ROOM TEMPERATURE')

    m39 = fields.Selection([('yes', 'Yes نعم'),
                            ('no', 'No لا')], 'Have you had a massage before?')
    m40 = fields.Char("When")
    m52 = fields.Char("1-  • Please list any physical or health conditions that your therapist should be aware")
    m53 = fields.Char(
        "2- • Please list any medication taken regularly and any specific medication / pain killer taken today?")
    m54 = fields.Char("3- •What would you like to gain from your treatment today?")
    m55 = fields.Char("4- • How many glasses of water ____caffeinated drinks ____do you drinking a day?")
    m56 = fields.Char("5- • What type of exercise are you doing regularly ____________ hrs per week ___?")
    m57 = fields.Selection([('Energetic', 'Energetic'),
                            ('Relaxed', 'Relaxed'),
                            ('Tired', 'Tired'),
                            ('Stressed', 'Stressed'),
                            ('pain', 'In Pain')], "6- • How do you feel today?")
    m58 = fields.Char("14- • Notes:")
    m59 = fields.Selection([('word', 'Word of mouth'),
                            ('media', 'Social Media'),
                            ('walkby', 'Walk by'),
                            ('website', 'Our Website')], "How did you hear about us?")
    m70 = fields.Binary(string='Customer Signature')
    m71 = fields.Binary(string='Administrative Signature')

    l1 = fields.Boolean('Pregnant/Breast feeding')
    l2 = fields.Boolean('Skin Sensitivity')
    l3 = fields.Boolean('Sensitive Eye')
    l4 = fields.Boolean('Recent operation')
    l5 = fields.Boolean('Diabetic Retinopathy')
    l6 = fields.Boolean('Alopecia')
    l7 = fields.Boolean('Dry eye syndrome')
    l8 = fields.Boolean('Trichotillomania')
    l9 = fields.Boolean('Epilepsy or Seizures')
    l10 = fields.Boolean('Asthma')
    l11 = fields.One2many('consent.lashes', 'consent_id', 'Lash Details')
    l12 = fields.Char('Lashes technician comments ملاحظات فني الررموش ')
    l70 = fields.Binary(string='Customer Signature')
    l71 = fields.Binary(string='Administrative Signature')

    def action_confirm(self):
        pass

    def action_print(self):
        return self.env['report'].get_action(self.id, 'ssquared_consent_management.report_consent')

