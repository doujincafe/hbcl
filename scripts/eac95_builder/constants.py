"""The constants used in translation."""

LINENUMBERS = [
    1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 31, 50, 51, 52, 1200, 1203, 1204, 1210,
    1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221, 1222,
    1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230, 1232, 1233, 1234, 1235,
    1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245, 1246, 1247,
    1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259,
    1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270, 1271,
    1272, 1273, 1274, 2501, 4270, 4271, 4272, 81700, 81701, 81702, 81703,
    81704, 81705, 81706, 81707, 81708, 81709, 81710, 81711, 81712, 81713,
    81714, 81715, 81716, 81717, 81718, 81719, 81720
]

SAMPLEPATTERN = {
    'drive': None,
    'settings': {
        'Read mode': None,
        'C2 pointers': None,
        'Accurate stream': None,
        'Audio cache': None,
        'Drive offset': 1256
    },
    'full line settings': {
        'Fill missing offset samples with silence': 1264,
        'Deleting silent blocks': 1265
    },
    'bad settings': {
        'Normalization': 1266,
        'Compression offset': 1262,
        'Combined offset': 1255
    },
    'proper settings': {
        'Fill missing offset samples with silence': 15,
        'Deleting silent blocks': 16
    },
    'range': 1210,
    'track': 1226,
    'track settings': {
        'filename': 1269,
        'pregap': 1270,
        'peak': 1217,
        'test crc': 1271,
        'copy crc': None
    },
    'track errors': {
        'Aborted copy': 1228,
        'Timing problem': 1212,
        'Missing samples': 1214,
        'Suspicious position': 1213
    },
    'footer': 1225,
}
