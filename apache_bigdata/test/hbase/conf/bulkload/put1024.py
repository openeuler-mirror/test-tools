import sys
from multiprocessing import Process


def make_data_byStage(begin, end, seed_name):
    f = open(seed_name, 'w')
    f.write('')
    f.close

    strb1 = '4470139980131260000'
    strc1 = '1000020110102156100651'
    strc2 = '^20110102^10000'
    strc3 = '^156^1^0065^20110102 01:36:19.998^CN000^0037000^4470139980131260000^0^20170401^57^156^1^^^^640120100DI00000010^02^0065^6217004470015729952^04^^^20170401^abcd^20170401^013619^20170401^013619^0000000000000.00^0000000000000.06^0000000000000.06^20^0000000007006.60^000000000007006.00^^999CCBSTLR640120100DI0^^640120100^^^^^^^^^^^^^^05^^0^^^^^CCBTR2180^^^0000000007006.60^0000000000000.00^0000000007006.60^000000000007006.60^0000000000000.00^0000000000000.00^0000000000000.00^0000000000000.00^0000000000000.00^0000000000000.00^0000000000000.00^0^0^2017-04-01^^CCBTR2180^0000000000000.00^0000000000000.00^20170401^2017-04-01 01:36:19.998^NX0000000^20190411^2019-04-01 13:41:20^NX000000000000^20150616^20150616 03:55:20^9^0000000000000.00^0000000000000.06^0000000000000.06^20^0000000007006.60^0000000007006.60^000000000007006.60^0000000000000.00^0000000000000.00^0000000000000.00^0^^0000000007006.60^00000000'

    if begin >= end:
        return

    for num in range(begin, end):
        wstr1 = "%032d" % num
        wstr2 = strb1
        wstrtmp = "%016d" % num
        wstr3 = strc1 + wstrtmp + strc2 + wstrtmp + strc3
        ww = wstr1 + ',' + wstr2 + ',' + wstr3
        f = open(seed_name, 'a')
        f.write(ww + '\n')

        f.close

    print
    'Generate data for' + seed_name + 'finished!'


def Usage():
    usage = "Usage: python put_data_byStage.py begin end filelist\n  \
    <begin> data start number \n  \
    <end> data end number \n  \
    <filelist> data file list\n  \
   example: python put_data_byStage.py 1 10 datafile1.csv datafile2.csv"
    print
    usage


if __name__ == "__main__":
    if len(sys.argv) < 4 or sys.argv[1] > sys.argv[2]:
        Usage()
        exit()

    begin = long(sys.argv[1])
    end = long(sys.argv[2])

    data_file_num = len(sys.argv) - 3
    quotient = (end + 1 - begin) / data_file_num
    remainder = (end + 1 - begin) % data_file_num
    print
    quotient, remainder
    numStartPointer = 0
    numEndPointer = begin
    for i in range(data_file_num):
        numStartPointer = numEndPointer
        if i < remainder:
            numEndPointer = numStartPointer + quotient + 1
        else:
            numEndPointer = numStartPointer + quotient

        ps = Process(target=make_data_byStage, args=(numStartPointer, numEndPointer, sys.argv[i + 3]))
        ps.start()
        print
        ps.name, ps.pid, "start generating data for " + sys.argv[i + 3] + " Num Range [" + str(
            numStartPointer) + "," + str(numEndPointer) + ")"

    print
    "Data generate STOP"
