#!/usr/bin/python

import sys
import copy
import itertools
from decimal import Decimal

'utilitu needed'
class Node:
   def __init__(self,name,des):
      self.parents=[]
      self.prob = {}
      self.decision=des
      self.name=name
   def setVariables(self,oldVariable,prob):
      self.parents=copy.deepcopy(oldVariable)
      self.prob=copy.deepcopy(prob)

class Query:
   def __init__(self,qtype):
      self.quieries={}
      self.given={}
      self.qtype=qtype
   def setVals(self,quieries,given):
      self.quieries=copy.deepcopy(quieries)
      self.given=copy.deepcopy(given)   

def printVal(net,qCltn):
   for val in range(0,len(net)):
      print net[val].name,net[val].parents,net[val].prob
   print "***************************"
   for q in qCltn:
      print q.qtype,q.quieries,q.given

def giveProb(q,BNetwork):
   result=[]
   sol=1
   for key, value in q.quieries.iteritems():
      newGiven=adConditionGiven(key,q.quieries,BNetwork)
      result.append(enumerationASK(key,value,q.given,BNetwork,newGiven))
   for val in result:
      sol=sol*val   
   return sol

def adConditionGiven(Akey,quieries,BNetwork):
   newGiven={}
   getNode=None
   for val in BNetwork:
      if val.name==Akey:
         getNode=copy.deepcopy(val)
   if getNode.parents:
      for key,value in quieries.iteritems():
         if key in getNode.parents:
            newGiven[key]=value
   return newGiven         
   
def enumerationASK(key,value,given,BNetwork,newGiven):
   for i in range(0,2):
      eList=copy.deepcopy(given)
      eList.update(newGiven)
      if i==0:
         eList[key]="+"
         plus=enumerateALL(BNetwork,eList)
      else:
         eList[key]="-"
         minus=enumerateALL(BNetwork,eList)
   if value=="+":
      valueReturned=plus/(plus+minus)
   else:
      valueReturned=minus/(plus+minus)
   'print valueReturned'
   return valueReturned

def enumerateALL(net,eList):
   if not net:
      return 1.0
   y=net[0]
   rest=net[1:]
   if y.name in eList:
      return (getProb(y,net,eList)* enumerateALL(rest,eList))
   else:
      alist=copy.deepcopy(eList)
      alist[y.name]="+"
      ans1= getProb(y,net,alist) * enumerateALL(rest,alist)
      alist=copy.deepcopy(eList)
      alist[y.name]="-"
      ans2= getProb(y,net,alist) * enumerateALL(rest,alist)
      return ans1+ans2    
   
def getProb(node,BNetwork,eList):
   nodeString=""
   if node.parents is None:
      if eList[node.name]=="-":
         if node.prob["+"]=="decision":
            return 0.00000001
         else:
            return (1-float(node.prob["+"]))
      else:
         if node.prob["+"]=="decision":
            return 1.0
         else:
            return float(node.prob["+"])
   else:
      for p in node.parents:
         if checkIfDesicionNode(p,BNetwork):
            if eList[p]=="+":
               nodeString+="+"
            else:
               nodeString+="-"
         else:
            nodeString+=eList[p]
      if eList[node.name]=="-":
         return (1-float(node.prob[nodeString]))
      else:
         return float(node.prob[nodeString])   

def checkIfDesicionNode(name,net):
   for node in net:
      if node.name==name and node.prob["+"]=="decision":
         return True
   return False       

def giveEU(q,BNetwork):
   eList=q.given
   for key,value in q.quieries.iteritems():
      eList[key]=value
   for val in BNetwork:
      if val.name=="utility":
         node=copy.deepcopy(val)
   parentProb={}
   util=0
   for parent in node.parents:
      parentNode=constructQuery(parent,"+",eList)
      parentProb[parent+"+"]=giveProb(parentNode,BNetwork)
      parentNode=constructQuery(parent,"-",eList)
      parentProb[parent+"-"]=giveProb(parentNode,BNetwork)
   '''if len(node.parents)==2:
      value=calUtil2(parentProb,node,node.parents)
   if len(node.parents)==1:
      value=calUtil1(parentProb,node,node.parents)
   if len(node.parents)==3:
      value=calUtil3(parentProb,node,node.parents)'''
   value=calUtil2(parentProb,node,node.parents)
   return value
   
   
def constructQuery(parent,occur,eList):
   query=Query("Prob")
   quieries={}
   quieries[parent]=occur
   query.setVals(quieries,eList)
   return query   

def calUtil2(parentProb,node,parents):
   '''values= list(itertools.product(('+-'), repeat=len(parents)))'''
   if len(parents)==1:
      values= list(itertools.product(('+-')))
   else:
      values= list(itertools.product(('+-'), repeat=len(parents)))
   result=[]
   for val in values:
      '''parent1=float(parentProb[parents[0]+val[0]])
      parent2=float(parentProb[parents[1]+val[1]])
      util=float(node.prob[val[0]+val[1]])
      result.append(parent1*parent2*util)'''
      parent=[]
      for i in range(0,len(parents)):
         parent.append(float(parentProb[parents[i]+val[i]]))
      string=''
      for i in val:
         string+=i
      util=float(node.prob[string])
      parProd=1
      for par in parent:
         parProd*=par
      result.append(parProd*util)
   sol=0
   for val in result:
      sol+=val
   return sol

def giveMEU(q,BNetwork):
   result={}
   queryNew=copy.deepcopy(q)
   if len(q.quieries)==1:
      values= list(itertools.product(('+-')))
   else:
      values= list(itertools.product(('+-'), repeat=len(q.quieries)))
   keyCollection=[]
   for key in q.quieries:
      keyCollection.append(key)
   for val in values:
      queryNew=copy.deepcopy(q)
      newQuery={}
      for i in range(0,len(keyCollection)):
         newQuery[keyCollection[i]]=val[i]
      queryNew.quieries=copy.deepcopy(newQuery)
      string=""
      'String has been reveresed before adding, to over come the differce between append and just adding key in front'
      for i in val:
         string+=i
      result[rev(string)]= (giveEU(queryNew,BNetwork))
   lKey=""
   lValue=0
   for key,value in result.iteritems():
      if lValue<value:
         lValue=value
         lKey=key
   lValue=int(round(lValue))
   return (" ".join(lKey)+" "+str(lValue))
   
def rev(s):
   return s[::-1]    
   
'''def calUtil3(parentProb,node,parents):
   values= list(itertools.product(('+-'), repeat=len(parents)))
   for val in values:
      parent1=float(parentProb[parents[0]+val[0]])
      parent2=float(parentProb[parents[1]+val[1]])
      parent3=float(parentProb[parents[2]+val[2]])
      util=float(node.prob[val[0]+val[1]+val[2]])
      result.append(parent1*parent2*parent3*util)
   sol=0
   for val in result:
      sol+=val
   return sol
      
def calUtil1(parentProb,node,parents):
   result=[]
   values= list(itertools.permutations('+-'))
   for vals in values:
      value1=float(parentProb[parents[0]+vals[0]])
      value3=float(node.prob[vals[0]])
      result.append(value1*value3)
   sol=0
   for val in result:
      sol+=val
   return sol'''


   
   
def main(fname):
   fo = open("output.txt", "a")
   qCltn=[]
   BNetwork=[]
   querRead=False
   with open(fname) as f:
      while True:
         line=f.readline()
         if not line: break
         if line.startswith("******"):
            querRead=True
            continue
         if line.startswith("***"):
            continue
         '''if the query has been read and the node has parent values'''
         if querRead:
            'if the qury is read, check if node has any parent nodes'
            if "|" in line:
               valueNames=line.split("|")
               name=valueNames[0].strip()
               parentNames=[]
               parentNameValues=valueNames[1].split(" ")
               for l in parentNameValues:
                  l=l.strip()
                  if not l=="":
                     parentNames.append(l.strip())
               probabilities={}
               for i in range(0,pow(2,len(parentNames))):
                  valueEntries=f.readline()
                  if not valueEntries: break                  
                  if line.startswith("******"):
                     querRead=True
                     continue
                  if line.startswith("***"):
                     continue
                  allValues=valueEntries.split(" ")
                  probName=""
                  for someVar in range(1,len(allValues)):
                     probName+=allValues[someVar].strip()
                  probabilities[probName]=allValues[0]
               node=Node(name,False)
               node.setVariables(parentNames,probabilities)
               BNetwork.append(node)
               'If no parent are given'
            else:
               name=line
               value=f.readline()
               if value=="decision":
                  value="decision"
               if not value: break
               if line.startswith("******"):
                  querRead=True
                  continue
               if line.startswith("***"):
                  continue
               node=Node(name.strip(),value)
               probabilities={}
               probabilities["+"]=value.strip()
               node.setVariables(None,probabilities)
               BNetwork.append(node)
            '''reading the query for the problem'''
         else:
            if line.startswith("P"):
               qtype="Prob"
            if line.startswith("EU"):
               qtype="EU"
            if line.startswith("MEU"):
               qtype="MEU"
            quieries={}
            givens={}
            if "|" in line:
               givenAsk=line.split("|")
               ask=givenAsk[0].split("(")[1].split(",")
               if qtype!="MEU":
                  for a in ask:
                     key=a.split("=")[0].strip()
                     value=a.split("=")[1].strip()
                     quieries[key]=value
               else:
                  for a in ask:
                     quieries[a.strip()]="NA"                  
               given=givenAsk[1].split(")")[0].split(",")
               for g in given:
                  gkey=g.split("=")[0].strip()
                  gvalue=g.split("=")[1].strip()
                  givens[gkey]=gvalue
            else:
               given=None
               ask=line.split("(")[1].split(")")[0].split(",")
               if qtype!="MEU":
                  for ak in ask:
                     akey=ak.split("=")[0].strip()
                     avalue=ak.split("=")[1].strip()
                     quieries[akey]=avalue
               else:
                  for ak in ask:
                     quieries[ak.strip()]="NA"  
            query=Query(qtype)
            query.setVals(quieries,givens)
            qCltn.append(query)
   for q in qCltn:
      if q.qtype=="Prob":
         res= Decimal(str(giveProb(q,BNetwork))).quantize(Decimal('.01')) 
      if q.qtype=="EU":
         res=(int(round(giveEU(q,BNetwork))))
      if q.qtype=="MEU":
         res=(giveMEU(q,BNetwork))
      fo.write(str(res))
      print res
      fo.write("\n")
                                    
   'printVal(BNetwork,qCltn)'
                                               
main(sys.argv[2])
