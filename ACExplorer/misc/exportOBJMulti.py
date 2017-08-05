import os
import json
from ACExplorer import CONFIG
from ACExplorer.ACUnity.decompressDatafile import decompressDatafile
from ACExplorer.ACUnity.exportTexture import exportTexture
from ACExplorer.ACUnity.getMaterialIDs import getMaterialIDs
from ACExplorer.ACUnity.readModel import readModel
from ACExplorer.misc import tempFiles


def exportOBJMulti(fileTree, fileList, rootID, fileIDList):
	#fileIDList format
	# {
	# 0:{'id':'0000000000000000', 'x':0, 'y':0, 'z':0},
	# 1:{'id':'0000000000000000', 'x':0, 'y':0, 'z':0},
	# 2:{'id':'0000000000000000', 'x':0, 'y':0, 'z':0}
	# }
	
	if not tempFiles.exists(rootID):
		decompressDatafile(fileTree, fileList, rootID)
	rootData = tempFiles.read(rootID)
	if len(rootData) == 0:
		raise Exception('file '+rootID+' is empty')
	rootData = rootData[0]
	
	# remove models that couldn't be read
	ticker = 0
	fileIDList2 = {}
	for index0 in fileIDList:
		fileID = fileIDList[index0]['id'].upper()
		
		if not tempFiles.exists(fileID):
			decompressDatafile(fileTree, fileList, fileID)
		data = tempFiles.read(fileID)
		if len(data) == 0:
			raise Exception('file '+fileID+' is empty')
		data = data[0]
		
		if not os.path.isfile(data['dir'].replace('.acu', '.json')):
			try:
				readModel(fileTree, fileList, fileID)
			except:
				print 'Failed reading model '+data['fileName']
		if os.path.isfile(data['dir'].replace('.acu', '.json')):
			fileIDList2[ticker] = fileIDList[index0]
			ticker += 1
			print 'read model '+str(ticker)+ ' of '+str(len(fileIDList))
	fileIDList = fileIDList2
	
	rootID = rootID.upper()
	fileName = rootData['fileName']
	savePath = CONFIG['dumpFolder'] + os.sep + fileName
	# savePath = path[:-4] + ".obj"
	# str1 = os.sep.join(savePath.split(os.sep)[:-1])	#save path folder
	# while (treeNode1.Parent != null)
		# treeNode1 = treeNode1.Parent;
	# string str2 = treeNode1.Tag.ToString().ToLower();					'acu'
	
	# obj file
	fio = open(savePath + ".obj", 'w')																		# open obj
	fio.write("# Wavefront Object File\n")														# write text
	fio.write("# Exported by ACExplorer based on code from ARchive_neXt\n")
	fio.write("mtllib " + fileName + ".mtl\n")
	fio.write('\n')
	offset = 0
	tempFileRepeat = {}
	
	# mtl file
	fim = open(savePath + ".mtl", 'w')
	fim.write("# Material Library\n")
	fim.write("# Exported by ACExplorer based on code from ARchive_neXt\n")
	fim.write("\n")
	idsAdded = []
	missingNo = False
	
	for index0 in fileIDList:
		fileID = fileIDList[index0]['id'].upper()

		if not tempFiles.exists(fileID):
			decompressDatafile(fileTree, fileList, fileID)
		data = tempFiles.read(fileID)
		if len(data) == 0:
			raise Exception('file '+fileID+' is empty')
		data = data[0]
		
		# used in face data section to define unique names
		if fileID not in tempFileRepeat:
			tempFileRepeat[fileID] = 0
		else:
			tempFileRepeat[fileID] += 1
		
		with open(data['dir'].replace('.acu', '.json')) as f:
			try:
				model = json.loads(f.read())
			except:
				print data['fileName']
				raise Exception()
			num2 = model['modelScale'] * 0.0002 * 10	# model scale
			num3 = 2048.0
			num4 = 0
			# if model['typeSwitch'] != 3:
				# num2 = 100.0
			# else:
				# num2 = 0.00305
				# num2 = 1
			
			# vertex data
			for vertex in model['vertData']['vertex']:
				#+(fileIDList[index0]['x']/100000.0)
				fio.write("v " +
				str(round((vertex['X'] * num2)+(fileIDList[index0]['x']), 6))
				
				+ " " +
				
				str(round((vertex['Y'] * num2)+(fileIDList[index0]['y']), 6))
				
				+ " " +
				
				str(round((vertex['Z'] * num2)+(fileIDList[index0]['z']), 6))
				
				+ '\n')
			print 'written vertex data '+str(index0)+ ' of '+str(len(fileIDList))
			
			# texture coordinates
			for tVert in model['vertData']['tVert']:
				fio.write("vt " + str(round((tVert['X'] / num3), 6)) + " " + str(round((tVert['Y'] / -num3), 6)) + '\n')
			print 'written texture coordinates '+str(index0)+ ' of '+str(len(fileIDList))
			
			# face mappings
			for index1, meshData in enumerate(model['meshData']):
				num5 = meshData['vertCount']		#vertex number?
				num6 = meshData['vertStart'] / 3
				if model['typeSwitch'] == 0 and model['faceCount'] != model['facesUsed']:
					if index1 > 0:
						num6 = num4 * 64
						num4 += model['meshFaceBlocks'][index1]
					else:
						num4 = model['meshFaceBlocks'][index1]
				fio.write("g " + data['fileName'] + "_" + str(tempFileRepeat[fileID]) + '_' +str(index1) + '\n')
				
				textureIDs = getMaterialIDs(fileTree, fileList, model['materialId'][index1])
				
				if textureIDs == None:
					fio.write("usemtl missingNo\n")
				else:
					for hexid in textureIDs:
						exportTexture(fileTree, fileList, textureIDs[hexid])
					data2 = tempFiles.read(model['materialId'][index1].upper())
					if len(data2) == 0:
						raise Exception('file '+model['materialId'][index1].upper()+' is empty')
					data2 = data2[0]
					material = data2['fileName']
					fio.write("usemtl " + material + '\n')
				fio.write("s 0\n")
				if model['typeSwitch'] != 3:
					num7 = meshData['X']
				else:
					num7 = 0
				for index2 in range(num6, num5 + num6):
					fio.write("f " + 
						str(int(model['faceData'][index2]['Y'] + 1.0 + num7 + offset)) + "/" + 
						str(int(model['faceData'][index2]['Y'] + 1.0 + num7 + offset)) + " " + 
						str(int(model['faceData'][index2]['X'] + 1.0 + num7 + offset)) + "/" + 
						str(int(model['faceData'][index2]['X'] + 1.0 + num7 + offset)) + " " + 
						str(int(model['faceData'][index2]['Z'] + 1.0 + num7 + offset)) + "/" + 
						str(int(model['faceData'][index2]['Z'] + 1.0 + num7 + offset)) + '\n')
				fio.write("# " + str(num5) + " triangles\n\n")
			offset += len(model['vertData']['vertex'])
			print 'written triangle data '+str(index0)+ ' of '+str(len(fileIDList))
			
			# material data in mtl
			for materialId in model['materialId']:
				if materialId in idsAdded:
					continue
				else:
					idsAdded.append(materialId)
					
				data2 = tempFiles.read(materialId.upper())
				if len(data2) == 0:
					raise Exception('file '+materialId.upper()+' is empty')
				data2 = data2[0]
				
				material = data2['fileName']
				if material != "NULL":
					textureIDs = getMaterialIDs(fileTree, fileList, materialId)
					
					if textureIDs == None:
						missingNo = True
						continue
					fim.write("newmtl " + material + '\n')
					fim.write("Ka 1.000 1.000 1.000\n")
					fim.write("Kd 1.000 1.000 1.000\n")
					fim.write("Ks 0.000 0.000 0.000\n")
					fim.write("Ns 0.000\n")
					for texType in textureIDs:
						if texType == 'diffuse':
							fim.write("map_Kd ")
						elif texType == 'normal':
							fim.write("bump -bm 0.300 ")
						elif texType == 'specular':
							fim.write("map_Ks ")
						else:
							continue
							
						data3 = tempFiles.read(textureIDs[texType].upper())
						if len(data3) == 0:
							raise Exception('file '+textureIDs[texType].upper()+' is empty')
						data3 = data3[0]
				
						fim.write(data3['fileName'] + '.dds\n')
						if texType == 'diffuse':
							fim.write("map_d ")
							fim.write(data3['fileName'] + '.dds\n')

					fim.write('\n')
			print 'written texture data '+str(index0)+ ' of '+str(len(fileIDList))
	
	fio.close()
		
	# write misingNo texture if used
	if missingNo:
		fim.write("newmtl missingNo\n")
		fim.write("Ka 1.000 1.000 1.000\n")
		fim.write("Kd 1.000 1.000 1.000\n")
		fim.write("Ks 0.000 0.000 0.000\n")
		fim.write("Ns 0.000\n")
		fim.write("map_Kd missingNo.png\n")
		fim.write('\n')
	fim.close()
	
	print 'done'
