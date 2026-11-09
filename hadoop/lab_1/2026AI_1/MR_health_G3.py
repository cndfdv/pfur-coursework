
#Average final grade G3 for each health level
from mrjob.job import MRJob

class MRmyjob(MRJob):
    def mapper(self, _, line):
        #Split the line with tab separated fields
        data=line.split(';')

        #Parse line
        health = data[28].strip()
        if health.isnumeric():
            G3 = int(data[32].strip())
            yield health, G3

    def reducer(self, key, list_of_values):
        count = 0
        total = 0.0
        for x in list_of_values:
            total += x
            count += 1
        avgLen = ("%.2f" % (total/count))
        yield key, avgLen

if __name__ == '__main__':
    MRmyjob.run()
