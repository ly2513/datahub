package DataHubORM;

import java.lang.annotation.Annotation;
import java.lang.reflect.Field;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;

import datahub.DHCell;
import datahub.DHData;
import datahub.DHField;
import datahub.DHQueryResult;
import datahub.DHRow;
import datahub.DHSchema;
import datahub.DHTable;
import datahub.DHType;

import Annotations.column;
import Annotations.column.Index;
import Annotations.database;
import Annotations.table;
import DataHubORMTests.TestModel;
import DataHubResources.Resources;

@table(name="")
public class Model<T extends Model>{
	
	
	private static Database db;
	
	@column(name="id")
	public int id;
	
	public Model(){
		this.id = 0;
		for(Field f: this.getClass().getFields()){
			if(DataHubConverter.isDataHubArrayListSubclass(f.getType())){
				try{
					DataHubArrayList d = (DataHubArrayList) f.getType().newInstance();
					d.setCurrentModel(this);
					d.setDatabase(db);
					Resources.setField(this, f.getName(), f.getType().newInstance());
				}catch(Exception e){
					
				}
			}
		}
	}
	public static void setDatabase(Database database) throws DataHubException{
		//TODO: figure out why this is getting set more than once
		db=database;
		/*if(db == null){
			db = database;
		}else{
			//throw new DataHubException();
		}*/
	}
	public static Database getDatabase(){
		return db;
	}
	public void save(){
		try{
			String query = "";
			//fix this
			if(this.id <= 0){
				query = "INSERT INTO "+this.getCompleteTableName()+"("+this.getFieldNames()+")"+" VALUES( "+getFieldValues()+")";
				//System.out.println(query);
			}else{
				query = "UPDATE "+this.getCompleteTableName()+" SET "+generateSQLRep()+" WHERE "+"id="+this.id;
			}
			getDatabase().query(query, this.getClass());
			//System.out.println(dhqr);
			updateModel();
		}catch(Exception e){
			e.printStackTrace();
		}
	}
	public void destroy(){
		try{
			String query = "DELETE FROM "+this.getCompleteTableName()+" WHERE "+"id="+this.id;
			//System.out.println(this.db.dbQuery("select * FROM "+this.db.getDatabaseName()+"."+this.getTableName()));
			//System.out.println(query);
			getDatabase().query(query, this.getClass());
			//possibly garbage collect object
		}catch(Exception e){
			e.printStackTrace();
		}
	}
	public ArrayList<T> all(){
		String query = "select * FROM "+this.getCompleteTableName();
		return (ArrayList<T>) getDatabase().query(query, this.getClass());
	}
	public ArrayList<T> findAll(HashMap<String,Object> params){
		String query = "select * FROM "+this.getCompleteTableName()+" WHERE "+ queryToSQL(params);
		return (ArrayList<T>) getDatabase().query(query, this.getClass());
	}
	public T findOne(HashMap<String,Object> params){
		String query = "select * FROM "+this.getCompleteTableName()+" WHERE "+ queryToSQL(params) +" LIMIT 1";
		if(getDatabase().query(query,this.getClass()).size() > 0){
			return (T) getDatabase().query(query,this.getClass()).get(0);
		}
		return null; 
	}
	private boolean hasFieldAndColumnBasic(String name){
		boolean out = false;
		try{
			Field f = this.getClass().getField(name);
			if(DataHubConverter.hasColumnBasic(f)){
				out= true;
			}
		}catch(Exception e){
			
		}
		return out;
	}
	private String queryToSQL(HashMap<String,Object> query){
		ArrayList<String> keyVal = new ArrayList<String>();
		for(String field:query.keySet()){
			if(hasFieldAndColumnBasic(field)){//also check if has column annotation
				String val = Resources.objectToSQL(query.get(field));
				keyVal.add(field+"="+val);
			}			
		}
		return Resources.concatenate(keyVal,"AND");
	}
	protected String generateSQLRep(){
		return generateSQLRep(",");
	}
	protected String generateSQLRep(String linkSymbol){
		HashMap<String,HashMap<String,DHType>> models = DataHubConverter.extractDataFromClass(this.getClass());
		HashMap<String,DHType> currentModel = models.get(this.getTableName());
		ArrayList<String> fieldData = new ArrayList<String>();
		for(String field:currentModel.keySet()){
			if(field!="id"){
				String val = Resources.getFieldStringRep(this,field);
				String entry = field+"="+Resources.objectToSQL(val);
				fieldData.add(entry);
			}
		}
		return Resources.concatenate(fieldData,linkSymbol);
	}
	protected String getFieldNames(){
		HashMap<String,HashMap<String,DHType>> models = DataHubConverter.extractDataFromClass(this.getClass());
		HashMap<String,DHType> currentModel = models.get(this.getTableName());
		ArrayList<String> fields = new ArrayList<String>();
		/*for(String oldField: currentModel.keySet()){
			String newField = getTableName()+"."+oldField;
			fields.add(newField);
		}
		return Resources.concatenate(fields,",");*/
		return Resources.concatenate(currentModel.keySet(),",");
	}
	protected String getFieldValues(){
		HashMap<String,HashMap<String,DHType>> models = DataHubConverter.extractDataFromClass(this.getClass());
		HashMap<String,DHType> currentModel = models.get(this.getTableName());
		ArrayList<String> fieldData = new ArrayList<String>();
		for(String field:currentModel.keySet()){
			fieldData.add(Resources.getFieldStringRep(this,field));
		}
		return Resources.converToSQLAndConcatenate(fieldData,",");
	}
	private void updateModel(){
		getDatabase().updateModelObject(this);
	}
	private T newInstance() throws InstantiationException, IllegalAccessException{
		return (T) getClass().newInstance();
	}
	public String getTableName(){
		table t = this.getClass().getAnnotation(table.class);
		if(t != null){
			return t.name();
		}
		return null;
	}
	public String getCompleteTableName(){
		return getDatabase().getDatabaseName()+"."+this.getTableName();
	}
}