import unittest
import tagfs.item_access as item_access
import systemMocks

class ParseTagsFromFileTest(unittest.TestCase):

    def setUp(self):
        super(ParseTagsFromFileTest, self).setUp()

        self.system = systemMocks.SystemMock(self)

    def setTagFileContent(self, lines):
        self.system.readFiles['.tag'] = systemMocks.ReadLineFileMock(lines)

    def assertParseTags(self, expectedTags):
        self.assertEqual(list(item_access.parseTagsFromFile(self.system, '.tag')), expectedTags)

    def testParseTagWithoutContext(self):
        self.setTagFileContent(['value',])

        self.assertParseTags([item_access.Tag('value'),])
