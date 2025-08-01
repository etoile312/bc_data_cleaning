import random
import datetime
from typing import List

class FieldSampler:
    def __init__(self, field_defs, logic_rules, drug_data=None):
        self.field_defs = field_defs
        self.logic_rules = logic_rules
        self.drug_data = drug_data

    def sample_segment(self, fields, n=100, group_name=None):
        if group_name == 'basic_info':
            return [self.sample_basic_info(fields) for _ in range(n)]
        if group_name == 'stage_and_metastasis':
            return [self.sample_stage_and_metastasis(fields) for _ in range(n)]
        if group_name == 'surgery':
            return [self.sample_surgery(fields) for _ in range(n)]
        if group_name == 'pathology':
            return [self.sample_pathology(fields) for _ in range(n)]
        if group_name == 'tumor_size':
            return [self.sample_tumor_size(fields) for _ in range(n)]
        if group_name == 'treatment':
            return [self.sample_treatment(fields) for _ in range(n)]
        if group_name == 'prognosis':
            return [self.sample_prognosis(fields) for _ in range(n)]
        if group_name == 'risk':
            return [self.sample_risk(fields) for _ in range(n)]
        if group_name == 'response':
            return [self.sample_response(fields) for _ in range(n)]
        if group_name == 'staging':
            return [self.sample_staging(fields) for _ in range(n)]
        return [self.sample_default(fields) for _ in range(n)]

    def sample_basic_info(self, fields):
        d = {}
        age = random.randint(18, 90)
        d['年龄'] = str(age)
        if age < 45:
            d['绝经状态'] = '否'
        elif age > 60:
            d['绝经状态'] = random.choice(['是', ''])
        else:
            d['绝经状态'] = random.choice(['是', '否'])
        d['PS'] = random.choice(['0','1','2','3','4','5',''])
        return {k: d.get(k, '') for k in fields}

    def sample_stage_and_metastasis(self, fields):
        d = {}
        # IV期、M1分期、远处转移、复发、转移位置、转移或复发
        d['IV期'] = random.choice(['是', '否'])
        d['M1分期'] = '是' if d['IV期'] == '是' else random.choice(['是', '否'])
        d['远处转移'] = '是' if d['IV期'] == '是' or d['M1分期'] == '是' else random.choice(['是', '否'])
        d['复发'] = random.choice(['是', '否'])
        # 转移位置
        if d['远处转移'] == '是' or random.random() < 0.3:
            n = random.randint(1, 3)
            d['转移位置'] = ','.join(random.sample(['肺', '肝', '骨', '脑', '其他'], n))
        else:
            d['转移位置'] = ''
        # 转移或复发
        if d['复发'] == '是' or d['远处转移'] == '是' or d['M1分期'] == '是' or d['转移位置']:
            d['转移或复发'] = '是'
        else:
            d['转移或复发'] = ''
        return {k: d.get(k, '') for k in fields}

    def sample_surgery(self, fields):
        d = {}
        d['是否保乳'] = random.choice(['是', '否', ''])
        d['已行根治手术'] = '是' if d['是否保乳'] == '否' else random.choice(['', '否'])
        d['可再次手术'] = random.choice(['是', '否', '']) if random.random() < 0.3 else ''
        d['切缘<1mm'] = random.choice(['是', '否'])
        d['切缘阳性'] = random.choice(['是', '否'])
        d['是否腋窝清扫'] = random.choice(['是', ''])
        d['腋窝淋巴结是否有阳性'] = random.choice(['是', '否'])
        d['腋窝淋巴结阳性个数(术前)'] = str(random.randint(0, 20)) if d['腋窝淋巴结是否有阳性'] == '是' else ''
        d['腋窝淋巴结阳性个数(术后)'] = str(random.randint(0, 20)) if d['是否腋窝清扫'] == '是' else ''
        if d['已行根治手术'] == '是':
            d['根治手术时间'] = (datetime.date.today() - datetime.timedelta(days=random.randint(0, 365*5))).strftime('%Y-%m-%d')
        else:
            d['根治手术时间'] = ''
        return {k: d.get(k, '') for k in fields}

    def sample_pathology(self, fields):
        d = {}
        d['组织学分级'] = random.choice(['高分化', '中分化', '低分化', ''])
        d['ER%'] = str(random.randint(0, 100))
        d['PR%'] = str(random.randint(0, 100))
        d['Her-2免疫组化'] = random.choice(['0', '1+', '2+', '3+', ''])
        d['FISH'] = random.choice(['未扩增', '扩增', ''])
        d['Ki-67%'] = str(random.randint(0, 100))
        return {k: d.get(k, '') for k in fields}

    def sample_tumor_size(self, fields):
        d = {}
        # 术前/术后各随机1-4项，数值1-13cm，术前>术后，数值相近
        pre_fields = ["术前肿块大小CM(MRI)", "术前肿块大小CM(CT)", "术前肿块大小CM(B超)", "术前肿块大小CM(查体)"]
        post_fields = ["术后肿块大小CM(MRI)", "术后肿块大小CM(CT)", "术后肿块大小CM(B超)", "术后肿块大小CM(查体)"]
        pre_n = random.randint(1, 4)
        post_n = random.randint(1, 4)
        pre_main = random.uniform(1, 13)
        post_main = max(0.5, pre_main - random.uniform(0.5, 4))
        for f in random.sample(pre_fields, pre_n):
            d[f] = round(random.uniform(max(1, pre_main-2), min(13, pre_main+2)), 1)
        for f in random.sample(post_fields, post_n):
            d[f] = round(random.uniform(max(0.5, post_main-2), min(pre_main, post_main+2)), 1)
        # 合成主字段
        def get_priority(keys, d):
            for k in keys:
                if k in d:
                    return d[k]
            return ''
        d['肿块大小CM(术前)'] = get_priority(pre_fields, d)
        d['肿块大小CM(术后)'] = get_priority(post_fields, d)
        return {k: d.get(k, '') for k in fields}

    def sample_treatment(self, fields):
        d = {}
        # 50%概率选择方案名称，50%概率用药品明细
        use_scheme = random.random() < 0.5
        scheme_options = [
            "TCbHP","THP","TCbH","TAC","AT","AC-T","TP","化疗 + PD-1/PD-L1 抑制剂","AI 类单药","AI+CDK4/6 抑制剂","氟维司群","OFS+AI","OFS+AI+CDK4/6 抑制剂","H","HP","T-DM1","TC+H","wTH","AC-TH","ddAC-ddT","FAC-T","FAC","X","AC","TC","TAM","OFS+TAM","吡咯替尼","奈拉替尼 + 卡培他滨","TXH","TH","NH","NX","吡咯替尼 + 卡培他滨","LX","拉帕替尼 + 曲妥珠单抗","TX","GP","GT","紫杉类单药","长春瑞滨","吉西他滨","依托泊苷","紫杉类 + 贝伐珠单抗","奥拉帕利","NP","艾立布林","优替德隆 + 卡培他滨","卡培他滨 + 贝伐珠单抗","氟维司群 + CDK4/6 抑制剂","OFS + 氟维司群","OFS + 氟维司群 + CDK4/6 抑制剂","AI + 西达本胺","AI + 依维莫司","OFS+AI + 西达本胺","孕激素","托瑞米芬","OFS + 孕激素","OFS + 托瑞米芬","OFS+AI + 依维莫司","唑来膦酸","伊班膦酸","地舒单抗","帕米磷酸二钠","XH","多西他赛","白蛋白紫杉醇","紫杉醇","TAM-AI","AC-TP","奈拉替尼","TAM+CDK4/6 抑制剂","OFS+TAM+CDK4/6 抑制剂","戈沙妥珠单抗","图卡替尼 + 卡培他滨","马吉妥昔单抗 + 化疗","T-Dxd","PD-1/PD-L1 抑制剂","大淋测试 update","H+TKI","TKI + 化疗","白蛋白紫杉醇 + 其他化疗","氟维司群 + AI","OFS + 氟维司群 + AI","骨保护","马吉妥昔单抗","阿贝西利","帕米膦酸二钠","伊尼妥单抗","TH + 吡咯替尼","TP + 帕博利珠单抗","氟维司群 + 依维莫司","阿培利司","抗 HER-2 单抗联合紫衫类为基础的其他方案如 AC-THP","蒽环联合紫衫方案：TAC、AT","科学、合理设计的临床研究如：抗 HER-2 ADC 等","以蒽环和紫衫为主的其他方案 AC-T","H + 内分泌治疗","部分乳腺短程照射 (APBI)","部分乳腺照射 (PBI)","全乳放疗 ± 瘤床加量","全乳单周超大方案","全乳放疗 ± 瘤床加量 + 区域淋巴结放疗","低复发风险患者可考虑豁免术后放疗","胸壁 ± 区域淋巴结放疗","是否延长 AI 治疗尚存争议","确定绝经者，可序贯使用 AI","未绝经者使用 TAM 或 OFS+AI","卡培他滨","H + 化疗","HP + 化疗","拉帕替尼 + 卡培他滨","甾体类 AI + 西达本胺","甾体类 AI + 依维莫司","甾体类 AI","TAM 或托瑞米芬","单药紫衫类：白蛋白紫杉醇、多西他赛、紫杉醇","单药治疗：卡培他滨、长春瑞滨、吉西他滨、依托泊苷","联合治疗：TX 方案、GT 方案、TP 方案","联合治疗：白蛋白紫杉醇 + PD-1 抑制剂、紫衫类 + 贝伐珠单抗","多柔比星脂质体","化疗 + PD-1 抑制剂","单药治疗：艾立布林、长春瑞滨、卡培他滨、吉西他滨","联合治疗：NP 方案、GP 方案、优替德隆 + 卡培他滨、NX 方案","单药治疗：白蛋白紫杉醇、戈沙妥珠单抗、依托泊苷","联合治疗：卡培他滨 + 贝伐珠单抗、白蛋白紫杉醇 + 其他化疗","全脑放疗","鞘内注射","HER-2 阳性患者，局部症状可控，可以在密切随访下考虑使用具","姑息对症支持治疗","脑转移最大径不超过 4cm，无明显占位效应 - SRS（适用于最大","全脑放疗 ± 海马回保护","fSRT","短程全脑放疗","手术切除 ± 术腔放疗","短程全脑放疗或 fSRT","全中枢放疗","胸壁 + 包括腋窝在内的区域淋巴结放疗","定期复查","内分泌治疗方案需要根据月经情况制定，请在病程管理中填写月经信","手术切除 + 术腔 SRS 或 fSRT","TP-AC 联合帕博利珠单抗","白蛋白紫杉醇 + PD-1 抑制剂","GP+PD-1 抑制剂","其他靶向药 + 内分泌"
        ]
        if use_scheme:
            num = random.randint(1, 2)
            d['药品信息'] = [s + '方案' for s in random.sample(scheme_options, num)]
        else:
            drug_map = {
                "化疗": ["卡铂", "多西他赛", "紫杉醇", "白蛋白紫杉醇", "表柔比星", "多柔比星", "环磷酰胺", "顺铂", "卡培他滨", "吉西他滨", "长春瑞滨", "氟尿嘧啶", "艾立布林", "奥拉帕利", "贝伐珠单抗", "依托泊苷", "优替德隆", "戈沙妥珠单抗", "甲氨蝶呤", "吡柔比星", "多柔比星脂质体", "紫杉醇脂质体"],
                "靶向治疗": ["曲妥珠单抗", "拉帕替尼", "T-DM1", "帕妥珠单抗", "吡咯替尼", "奈拉替尼", "伊尼妥单抗", "T-Dxd", "图卡替尼", "马吉妥昔单抗"],
                "内分泌治疗": ["阿那曲唑", "来曲唑", "依西美坦", "氟维司群", "TAM", "托瑞米芬", "依维莫司", "甲地孕酮", "甲羟孕酮", "西达本胺", "阿贝西利", "哌柏西利", "达尔西利", "瑞波西利", "阿培利司"],
                "免疫治疗": ["帕博丽珠单抗", "特瑞普利单抗", "卡瑞丽珠单抗", "替雷利珠单抗"]
            }
            drug_info = []
            for cat, drug_list in drug_map.items():
                if random.random() < 0.5:
                    num_drugs = random.randint(1, min(3, len(drug_list)))
                    drugs = random.sample(drug_list, num_drugs)
                    for drug in drugs:
                        drug_info.append({"药品名称": drug, "药品类别": cat})
            d['药品信息'] = drug_info
        d['免疫禁忌'] = random.choice(['是', '否', ''])
        d['有新辅助治疗'] = random.choice(['是', '否', ''])
        if d['有新辅助治疗'] == '是':
            d['新辅助治疗使用免疫'] = random.choice(['是', '否'])
            d['新辅助治疗使用双靶'] = random.choice(['是', '否'])
        else:
            d['新辅助治疗使用免疫'] = ''
            d['新辅助治疗使用双靶'] = ''
        return {k: d.get(k, '') for k in fields}

    def sample_prognosis(self, fields, stage_and_metastasis=None):
        d = {}
        # 采样根治手术时间
        min_year, max_year = 2010, 2025
        base_year = random.randint(min_year, max_year-1)
        base_month = random.randint(1, 12)
        base_day = random.randint(1, 28)
        base_date = datetime.date(base_year, base_month, base_day)
        d['根治手术时间'] = base_date.strftime('%Y-%m-%d')
        # 复发与否逻辑
        if stage_and_metastasis and '复发' in stage_and_metastasis:
            has_recur = stage_and_metastasis['复发'] == '是'
        else:
            has_recur = random.random() < 0.5
        if has_recur:
            recur_delta = random.randint(6, 60)
            recur_date = base_date + datetime.timedelta(days=recur_delta*30)
            if recur_date.year > max_year:
                recur_date = base_date + datetime.timedelta(days=12*30)
            d['复发时间'] = recur_date.strftime('%Y-%m-%d')
            d['DFS（月）'] = str((recur_date.year - base_date.year) * 12 + (recur_date.month - base_date.month))
        else:
            d['复发时间'] = ''
            d['DFS（月）'] = ''
        return {k: d.get(k, '') for k in fields}

    def sample_risk(self, fields):
        d = {}
        d['基因高风险'] = random.choice(['是', '否', ''])
        return {k: d.get(k, '') for k in fields}

    def sample_response(self, fields):
        d = {}
        d['pCR'] = random.choice(['是', '否', ''])
        d['ypT0N0'] = '是' if d['pCR'] == '是' else random.choice(['否', ''])
        d['MP评分'] = str(random.randint(1, 5)) if d['pCR'] == '是' or random.random() < 0.5 else ''
        return {k: d.get(k, '') for k in fields}

    def sample_staging(self, fields):
        d = {}
        d['cTNM'] = random.choice(['cT1N0M0', 'cT2N1M0', 'cT3N2M0', 'cT4N3M1', ''])
        d['pTNM'] = random.choice(['pT1N0M0', 'pT2N1M0', 'pT3N2M0', 'pT4N3M1', ''])
        d['ypTNM'] = random.choice(['ypT0N0', 'ypT1N1M0', 'ypT2N0M0', 'ypT2N2M0', 'ypT3N3M1', ''])
        return {k: d.get(k, '') for k in fields}

    def sample_default(self, fields):
        d = {}
        for field in fields:
            info = self.field_defs.get(field, {})
            d[field] = self.sample_field(field, info)
        return d

    def sample_field(self, field, info):
        if "min" in info and "max" in info:
            try:
                min_v, max_v = int(info["min"]), int(info["max"])
                return str(random.randint(min_v, max_v))
            except (ValueError, TypeError):
                pass
        options = info.get('options', [])
        if options:
            return random.choice(options)
        return info.get('default', '')