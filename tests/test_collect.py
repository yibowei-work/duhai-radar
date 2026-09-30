import unittest

from scripts.collect import canonicalize_url, classify_category, classify_impact, clean_text, has_chinese_text


class CollectorTests(unittest.TestCase):
    def test_canonical_url_removes_tracking(self):
        value = canonicalize_url("https://Example.com/story/?utm_source=x&b=2&a=1#section")
        self.assertEqual(value, "https://example.com/story?a=1&b=2")

    def test_html_is_removed(self):
        self.assertEqual(clean_text("<p>品牌 <strong>进入</strong> 新市场</p>"), "品牌 进入 新市场")

    def test_chinese_text_detection(self):
        self.assertTrue(has_chinese_text("希音在欧洲开设新门店"))
        self.assertFalse(has_chinese_text("New store opens in Europe"))

    def test_category_keywords(self):
        self.assertEqual(classify_category("new warehouse and fulfillment network", "品牌与扩张"), "物流与履约")
        self.assertEqual(classify_category("包装材料合规更新", "品牌与扩张"), "产品与包装")

    def test_impact_keywords(self):
        self.assertEqual(classify_impact("brand opens a new market"), "opportunity")
        self.assertEqual(classify_impact("product recall warning"), "risk")


if __name__ == "__main__":
    unittest.main()
