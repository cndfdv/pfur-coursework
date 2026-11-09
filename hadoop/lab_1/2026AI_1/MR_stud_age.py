
#Total number of students for each age
from mrjob.job import MRJob

class MRmyjob(MRJob):
    def mapper(self, _, line):
        #Split the line with semicolon separated fields
        data=line.split(';')

        #Parse line
        age = data[2].strip()

        #Emit age and 1
        if age.isnumeric():
            yield age, 1

    def reducer(self, key, list_of_values):
        yield key,sum(list_of_values)

if __name__ == '__main__':
    MRmyjob.run()
