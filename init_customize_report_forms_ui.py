# -*- coding: utf-8 -*-
import os
import shelve


if __name__ == '__main__':
    customize_report_forms_ui = shelve.open("{}/fotolei-pssa/tmp-files/customize_report_forms_ui".format(
        os.path.expanduser("~")), flag='c', writeback=False)
    customize_report_forms_ui["classification1_tags"] = ['数码', '传统耗材']
    customize_report_forms_ui["classification1_classification2_tags"] = [
        '数码|背带',
        '数码|包&收纳',
        '数码|快挂',
        '传统耗材|暗房冲洗设备',
        '传统耗材|胶片',
        '传统耗材|页片',
        '传统耗材|相纸',
        '传统耗材|彩色药水',
        '传统耗材|黑白药水',
        '传统耗材|底片收纳保护',
        '传统耗材|翻拍器',
        '传统耗材|放大机类',
        '传统耗材|胶片相机'
    ]
    customize_report_forms_ui["classification1_topk_tags"] = ['数码|top2', '传统耗材|top10']
    customize_report_forms_ui["brand_tags"] = [
        '百得信',
        '宝图',
        '福马',
        '富士',
        '柯达',
        '派森',
        '上海',
        '泰特诺',
        '伊尔福',
        'adox',
        'jobo',
        'lab-box',
        'osiris',
        'poilotfoto'
    ]
    customize_report_forms_ui["brand_topk_tag"] = 'top10'
    customize_report_forms_ui["brand_classification2_tags"] = []
    customize_report_forms_ui.close()
