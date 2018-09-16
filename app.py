from flask import Flask,render_template,url_for,request,g,redirect
import pymongo

app = Flask(__name__)


DB_NAME = 'foosball'  
DB_HOST = 'ds257752.mlab.com'
DB_PORT = 57752
DB_USER = 'badcoder123' 
DB_PASS = 'badal123'

connection = pymongo.MongoClient(DB_HOST, DB_PORT)
db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)

col_names =  ['rank','teamName', 'wins', 'loss' ,'points']

@app.route('/index')
def index():
	team = db.team
	cursor = team.find().sort('score' , -1)
	List = []
	i=1;
	for doc in cursor:
		List.append([i,doc["teamName"],doc["totalMatches"],doc["wins"],doc["loss"],doc["score"]])
		i = i+1

	while(i<=5):
		List.append(["","","","","",""])
		i = i+1
	print(List)
	return render_template('index.html',leaderboard=List)


@app.route('/leaderBoard')
def leaderBoard():
	return 'Hello, World!'

@app.route('/addMatchResult' , methods = ['POST'])
def addMatchResult():
	team = db.team
	comment = ''
	legalMatch = True

	if not request.form['goalA'].isdigit() or not request.form['goalB'].isdigit():
		comment = 'Invalid Details '
		legalMatch = False

		if request.form['teamA'] == request.form['teamB']:
			comment = 'Invalid Team Names'
			legalMatch = False

			if  int (request.form['goalA']) == int (request.form['goalB']):
				comment = 'Invalid Details '
				legalMatch = False

				if  int (request.form['goalA']) != 10 and int (request.form['goalB']) != 10:
					comment = 'Invalid Details '
					legalMatch = False

					if  int (request.form['goalA']) > 10 or int (request.form['goalB']) > 10:
						comment = 'Invalid Details '
						legalMatch = False


	existTeamB = team.find_one({'teamName' : request.form['teamB']})
	if existTeamB is None:
		comment = 'Team B not found'
		legalMatch = False

	existTeamA = team.find_one({'teamName' : request.form['teamA']})
	if existTeamA is None:
		comment = 'Team A not found'
		legalMatch = False

	if legalMatch:
		totMatchesA = int (existTeamA['totalMatches']) + 1
		gsA = int (existTeamA['goalsScored']) + int (request.form['goalA'])
		gaA = int (existTeamA['goalsAquire']) + int (request.form['goalB'])
		winsA = int (existTeamA['wins'])
		lossA = int (existTeamA['loss'])
		scoreA = int (existTeamA['score'])

		totMatchesB = int (existTeamB['totalMatches']) + 1
		gsB = int (existTeamB['goalsScored']) + int (request.form['goalB'])
		gaB = int (existTeamB['goalsAquire']) + int (request.form['goalA'])
		winsB = int(existTeamB['wins'])
		lossB = int (existTeamB['loss'])
		scoreB = int (existTeamB['score'])

		if int (request.form['goalA']) == 10:
			winsA = winsA + 1
			lossB = lossB + 1
			scoreA = scoreA + 3;
		elif int (request.form['goalB']) == 10:
			winsB = winsB + 1
			lossA = lossA + 1
			scoreB = scoreB + 3

		team.update_one({'teamName' : request.form['teamA']},{'$set':{'wins': winsA , 'loss':lossA , 'goalsScored' : gsA , 'goalsAquire' : gaA , 'totalMatches' : totMatchesA , 'score' : scoreA}})

		team.update_one({'teamName' : request.form['teamB']},{'$set':{'wins': winsB , 'loss':lossB , 'goalsScored' : gsB , 'goalsAquire' : gaB , 'totalMatches' : totMatchesB , 'score' : scoreB}})

		return redirect(url_for('index'))
	print(comment)
	cursor = team.find().sort('score' , -1)
	List = []
	i=1;
	for doc in cursor:
		List.append([i,doc["teamName"],doc["totalMatches"],doc["wins"],doc["loss"],doc["score"]])
		i = i+1

	while(i<=5):
		List.append(["","","","","",""])
		i = i+1

	return render_template('index.html',leaderboard=List,comment=comment)

@app.route('/home')
def home():
	return render_template('team.html',comment='')


@app.route('/addTeam' , methods=['POST'])
def addTeam():

	team = db.team
	comment = 'Team successfully created.'
	teamToBeAdded = True

	if request.form['teamName'] == '' or request.form['player1'] == '' or request.form['player2'] == '':
		teamToBeAdded = False
		comment = 'Invalid Details'

	if teamToBeAdded:
		cursor = team.find()
		for doc in cursor:
			if doc["teamName"] == request.form['teamName']:
				comment = "Team name already exists. "
				teamToBeAdded = False

	if teamToBeAdded:
		team.insert({'teamName' : request.form['teamName'] , 'player1' : request.form['player1'], 'player2' : request.form['player2'] ,'totalMatches' : 0, 'wins' : 0, 'loss' : 0, 'goalsScored' : 0,'goalsAquire' : 0 , 'score' : 0})

	return render_template('team.html',comment=comment)


@app.route('/getTeams' , methods=['GET'])
def get_teams():
	team = db.team
	allTeams = team.find_one({'teamName' : "Real Madrid"})
	return allTeams


if __name__ == "__main__":
  app.run(debug=True)

