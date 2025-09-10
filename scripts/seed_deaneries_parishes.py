from config.db import SessionLocal
# Explicitly import all models to register relationships
import models.deanery
import models.parish
import models.user
import models.outstation
import models.zone

from models.deanery import Deanery
from models.parish import Parish
from models.outstation import Outstation
# Map of deanery to list of parishes

def seed_data():
    seed_data = {
        "EASTERN DEANERY": {
            "Christ The King Embakasi" : ["St. John the Evangelist Tassia"], 
            "St. Monica Njiru" : ["St. Michael", "St. Rita", "St. Stephen", "St. Josephat"], 
            "St. Joseph Freinadimetz Ruai" : ["St. Cecilia", "St. Gabriel", "St. Josephine Bakhita"], 
            "St. Peter Ruai" : ["St. Kizito", "Holy Spirit"],
            "St. Anne & Joachim Soweto" : [], 
            "St. Vincent de Paul Kamulu" : ["St. Justin", "St. John Paul II", "St. Mary's"], 
            "Mary Immaculate Mihango" : [],
            "Holy Family Utawala" : ["St. Patrick's Mavoko"], 
            "Divine Word, Kayole" : [], 
            "St. Daniel Comboni" : [], 
            "St. Arnold Janssen Komarock" : []
        },
        "OUTERING DEANERY": {
            "St. Jude Donholm": ["St. Andrew Edelvale"], 
            "Holy Innocents Tassia" : ["Blessed Benedict Daswa"], 
            "Holy Trinity Kariobangi North": ["St.Daniel Comboni", "St. John the Baptist"],
            "Divine Mercy Kariobangi South" : ["Mary Immaculate Catholic Church"], 
            "St. Andre Bassette Dandora" : [], 
            "Assumption of Mary Umoja" : ["St. Veronica", "St. Teresa of Calcutta"],
            "Holy Cross Dandora" : []
        },
        "RUARAKA DEANERY": {
            "St. Dominic Savio, Mwiki" : ["St. Jeanne Jugaw"], 
            "St. Benedicts Survey" : ["St. Stephen", "St. Maurus", "St. John","St. Lwanga", "St. Thomas and Patrick"], 
            "St. Claire Kasarani" : ["St. Peter & Paul Cieko"],
            "Madre Teresa of Calcutta, Zimmerman" : [], 
            "Sacred Heart Babadogo" : ["St. Josephine Bakhita"], 
            "Queen of Apostles Ruaraka" : ["St. Gabriel Thome", "St. Mary's Marurui"]
        },
        "GITHURAI DEANERY": {
            "St. Joseph Mukasa Kahawa West" : ["St. Peter & Paul", "St. Francis of Assisi"], 
            "St. Francis of Assisi Mwihoko" : [], 
            "St. Joseph the Worker Kahawa Sukari" : ["Kahawa Wendani"],
            "Our Lady Consolata Kahawa Farmers" : ["St. Joseph Allamano Kiukenda"], 
            "Christ The King Kimbo" : [], 
            "St. Lucia Membley" : ["St. John Paul II", "St. Clare", "St. Teresa of Calcutta"], 
            "Holy Mary Mother of God Githurai" : ["St. Francis of Assisi Githurai","St. Mary Magdalene Njathaini"]
        },
        "MANGU DEANERY": {
            "St. Teresa Gachege" : [], 
            "St. Anne Mataara" : ["St. Anne Mariaini","St. Patrick’s Gichagi","St. Peter & Paul Miugu","St. May Muchakai","St. John Njatha-ini"], 
            "St. Peter Nyamangara" : ["St. john Miteru","St. Anne Mukurwe","St. Joachim Kangio","Mary Immaculate Mukuyu-ini","St. Elizabeth Banguro"], 
            "St. John the Baptist Mangu": ["St. Mary Igegania","St. Ann Mutuma","St. Archangel Gabriel Kawira","St. Arch Michael Makwa","St. Teresa of child Jesus Mwea"],
            "Our Lady of Fatima Kiriko" : [], 
            "St. Teresa Kiangunu" : ["St. John Buchana","St. Stephen Ndiko","St. John Gathanji","St. Martin Gakoe","Holy Trinity Mugumo-ini","St. Joseph Barigitu","St. Nicholas Raini","St. Theophilus Mwimuto","Our Lady Queen Gathuru"], 
            "St. Stephen Kairi" : ["St. John the Baptist Magumu","St. Peter & Paul Muirigo","St. John the Evangelist Gaithigi","St. Mary’s Kagambwa "], 
            "Our Lady of the Holy Rosary Kamwangi" : ["St. Simon Cimbici","St. Mathew Kariua","St. Mary Immaculate Kombirire"]
        },
        "GATUNDU DEANERY": {
            "Our Lady of Annunciation Gatitu" : ["Holy Trinity Muhoho", "St. James Kagera" , "St. James Kigaa", "Queen of Peace Nembu", "St. Patrick’s Gitamaiyu"], 
            "Matyrs of Uganda Gatundu" : ["St. Peter & Paul Muthiga" , "St. Charles Lwanga Muthiga", "Archangel Michael Githaruru" , "St. Patrick’s Icaciri" ,"Handege"], 
            "Christ The King Karinga": [], 
            "St. Joseph Kiganjo" : ["St. Teresa of Avilla Kiamwangi", "St. Lawrence Gatahi","St. Dominic Ikuma" , "St. Veronica Mutimumu"],
            "Archangel Gabriel Mutomo" : ["St. Joseph the worker Kimunyu","Holy Spirit Kahugu-ini","St. George Gachoka","Christ the King Gathage","Mary Immaculate Gitundu","St. George Ithingu","St. Paul Miki Karembu"], 
            "St. John the Baptist Munyu-ini": ["St. Mark Gathondo","St. Mathias Mulumba Gacharage","St. Joseph the worker Roi"], 
            "St. Stephen Ituru" : ["St. Vincent de Paul Gatei", "St. Mary Immaculate Wamwangi", "St. Joseph Mbichi"], 
            "St. Joseph Mutunguru" : [],
            "Mary Help of Christians Ndundu" : ["St. Joseph Kiamworia", "Christ the King Gachika", "St. Paul Gitare", "St. Camillus Gathiriga","St. John Paul II Karangi","St. Jude Gathiru","St. Peter Gaturia-maru","Our Lady Queen of the Holy Rosary Mundoro"]
        },
        "THIKA DEANERY": {
            "St. Patrick's Thika" : ["St. Peter the Rock","St. Francis of Assisi Athena"], 
            "St. Bernadette Ngoigwa" : ["St. Luke","St. Andrew's","St. Ann & Joachim"], 
            "St. Mathias Mulumba Makongeni" : ["St. Ambrose Kabuka","St. Joseph Mukasa","St. Gonzaga Gonza", "St. Andrew Kagwa"], 
            "St. Maria Magdalena Munyu" : ["Nativity of our Lord","St. Francis Xavier Komo","Our Lady of Assumption","Divine Mercy"],
            "St. Achilles Kiwanuka" : [], 
            "Holy Rosary Witeithie" : ["St. Helena Rurii", "St. Stephen Nyacaba"], 
            "Immaculate Conception Kilimambogo" : ["St. Luke Magogoni","Christ The King Ngoliba","St. Joseph the Worker Ndula"]
        },
        "RUIRU DEANERY": {
            "St. Teresa Kalimoni" : ["Holy Archangel", "St. Dominic"],
            "St. Francis of Assisi Ruiru" : ["St. Michael","St. Paul's", "St. Teresa's", "St. Gabriel", "St. Monica", "St. Martin", "St. Andrew", "St. Thomas"," St. James", "St. Charles Lwanga"], 
            "St. Christopher Kimbo" : ["St. Stephen the Martyr","St. Dominic"], 
            "Presentation of the Lord Juja Farm" : ["Queen of Holy Rosary", "St. Michael", "St. Joseph", "St. George","Mary Mother of God"],
            "St. Peter Kwihota" : ["St. Joseph", "St. Mark", "St. Cecilia", "St. Camillus", "Our Lady of Fatima"], 
            "St. Augustine Juja" : ["St. Paul's Gachororo", "Mary Mother of God"], 
            "Mary Immaculate Kumura":  ["Annunciation of the Lord", "St. Mark Theta", "Our Lady of Mercy", "St. Anne Ndururumo", "Our Lady of Consolata", "Holy Guardian Angels","St. John the Baptist"],  
            "Divine Mercy Kalimoni" : ["St. Anthony of Padua"], 
            "St. Paul Mugutha" : ["St. James", "St. Martin", "St. Michael", "St. Teresa"]
        },
        "MAKADARA DEANERY": {
            "Holy Trinity Buruburu" : ["St. Cecilia Kiambiu"], 
            "St. Teresa Eastleigh" : ["St. John Paul","St. Veronica"], 
            "St. Joseph Jericho" : [], 
            "St. Joseph & Mary Shauri Moyo" : [],
            "Our Lady of Visitation Makadara" : ["St. Charles Lwanga Bahati"], 
            "St. Mary Mukuru" : ["St. Bakhita", "St. Monica", "Holy Spirit", "St. Joseph", " St. Jude"], 
            "St. Mary Magdalene Kariokor" : [], 
            "Blessed Sacrament Buruburu" : []
        },
        "WESTERN DEANERY": {
            "Sacred Heart Dagoretti" : ["St. Vincent Pallotti", "St. Francis of Assisi Gatina","Sacred Heart Ngando","Blessed Elizabetta Praying Centre"], 
            "Regina Caeli Karen" : ["St. John Karinde"], 
            "Christ The King Kibera" : ["St. Gabriel Soweto", "St. Daniel Comboni Shilanga", "Divine Mercy Lindi", "St. Jude Highrise"], 
            "Our Lady of Guadalupe" : ["Our Lady of Lourdes","St. Luke","St. Thomas"],
            "St. John Langata" : ["Divine Mercy Kuwinda", "Shrine of the Apostles","MultiMedia University","Co-Operative University"], 
            "St. Michael Otiende" : [], 
            "Mary Queen of Apostles Dagoreti" : ["St. Joseph", "St. Jude", "St. Catherine","St. Vincent Pallotti"]
        },
        "CENTRAL DEANERY": {
            "Holy Family Basilica" : [], 
            "St. Francis Xavier Parklands" : [], 
            "St. Paul Chaplaincy" : [], 
            "St. Peter Clavers" : [],
            "Donbosco Upperhill" : [], 
            "Our Lady Queen of Peace South B" : ["St. Margaret Hazina"], 
            "St. Catherines of Alexandria South C" : ["St. Joseph"]
        },
        "KABETE DEANERY": {
            "St. Raphael Kabete" : [], 
            "St. Joseph Kangemi" : ["Christ The King"], 
            "St. Catherine Sienna" : ["St. Martin De Porres", "UON Lower Kabete Campus"], 
            "Holy Rosary Ridgeways" : ["St. Joseph Muringa", "St. Monica Huruma", "St. Charles Lwanga"],
            "Consolata Shrine" : [], 
            "Holy Trinity Kileleshwa" : [], 
            "St Austin Msongari" : []
        },
        "KIAMBU DEANERY": {
            "St. Stephen Gahie": ["St. Joseph Allamano Ruaka","St. Francis of Assisi Ndenderu","St. Anne Karura","St. Peter & Paul Kihara","St. Jose Maria Escriva Munyaka","St. Mother Teresa Kagongo","St. Mary’s Kianjogu" ], 
            "St. Joseph Gathanga": ["St. Stephen","St. Mary’s"], 
            "Holy Rosary Ikinu": ["Christ the King Gathanje","Holy Family Kiaibabu","St. Emmanuel Gathaithi","Mary Mother of God Kamondo","St. Jude Gathanje West","Emmanuel Catholic Gathaithi"], 
            "St. Martin de Porres Karuri" : ["Mary Immaculate Muchatha","St. Patrick Kiambaa","St. Peter Njoro","St. Monica Raini"],
            "St. Peter & Paul Kiambu" : ["St. Mary Immaculate Riabai","St. Joseph the Worker Gichocho","St. Gregory the great Thindingwa","St. Agnes Kangoya"], 
            "Our Lady of Victories Lioki" : ["Sacred Heart of Jesus Karia","St. Pius Ngemwa"], 
            "All Saints Riara" : ["St. Anne & Joachim Karunga","Our Lady of Fatima Ndumberi","Mary immaculate Kanunga","Sacred heart of Jesus Kawaida","St. Teresa of Child Jesus Ngegu","St. Thomas Aquinas Kasphat","St. John the  Baptist Njunu"], 
            "Our Lady of Rosary Ting'ang'a" : ["Divine Mercy Thaara","St. John the Baptist Ngaita"],
            "Holy Family Mugumo" : ["St. Simon Kiloma"]
        },
        "LIMURU DEANERY": {
            "Our Lady of Mt. Carmel Ngarariga":["St. Teresa Murengeti","St. Augustin Gitithia","St. Jude Kibagare"], 
            "St. Joseph the Worker Kereita":["St. Peter the Rock Kimende","St. Peter Clavers Magina","St. Joachim Kingatua","St. John Kinale","St. Ann Kamae","St. John Paul II Sulmac","St. Bartholomew "], 
            "St. Charles Lwanga Kamirithu Parish":["St. Joseph Tharuni","St. Peter Ndiuni","St. Teresa Rwamburi"],
            "St. Joseph Loreto":["St. Monica Karanjee","St. John Kabuku","St. James Redhill"], 
            "St. Andrews Rironi":[], 
            "St. Charles Lwanga Githirioni":["St. Joseph Kirenga","St. Joseph Matathia","St. John the Baptist Kwaregi","Sacred Heart Uplands","Escarpment"], 
            "St. Francis of Assisi Limuru":[]
    },
        "KIKUYU DEANERY": {
            "Immaculate Conception Gicharani" : ["Christ the King Nachu","St. Maria Gorretti Baraniki","St. Kizito Thogoto","St. Joseph Kiriti","St. Mark Ruthigiti","Our Lady of Assumption Mahia-ihi"], 
            "Holy Eucharist King'eero" : ["St. Joseph Allamano Kiahuria","St. Joseph Mwimuto","St. Francis of Assisi Kabete","St. John Evanelist Gathiga","St. John the Baptist Karura"], 
            "St. John the Baptist Riruta":[],
            "Our Lady of the Holy Rosary Ruku": ["St. Teresa Ngecha","St. Paul Gikuni","St. Mary Nyathuna"], 
            "St. Charles Lwanga Waithaka": ["Sacred Heart Ruthimitu"], 
            "St. Peter the Apostle Kikuyu":["St. Anne Muthure","St. Lucy Kanyariri","St. Augustine Ondiri","Mary Immaculate Gitaru","St. Paul’s Magoko"],
            "St. Joseph Kerwa":["St. Charles Lwanga Kari","St. Mary Nguriunditu","St. Philomena Nduma"], 
            "St. Joseph the Worker Muguga":[], 
            "Holy Cross Thigio":["Corpus Christi Nderu","Holy Spirit Makutano","St. Patrick’s Renguti","St. ann Nguirubi","St. Dominic Ndiguini","St. George Gitutha","Our Lady of Miraculous Kianjagi"], 
            "St. Peter the Rock Kinoo":[]
        },
        "GITHUNGURI DEANERY": {
            "Holy Family Githunguri" : ["Mary Immaculate Geteti","St. Francis Minja","St. Paul’s Ndeithia","St. John Jamaica","Kamuchege Sacred heart","Nyambururu St. Patrick’s","Good shepherd","Holy Family","Kindika","St. Lawrence Kareinga"], 
            "Nativity of our Lord Kagwe" : [], 
            "Our Lady of Assumption Kambaa" : ["St. John the Baptist Gitiha","St. Mary’s Gataka","St. Clare Iria-ini","St. Teresa Mathanja"],
            "All Saints Komothai":["St. Mary Githima","St. Francis Githioro","St. Paul Gathugu","St. John Bosco", "Our Lady of the Rosary Kibichoi","St. Joseph Gitombo","St. Jude Nginduri","St. Peter & Paul Kigumo","St. Anthony Thuita","St. Stephen Taara"], 
            "Holy Spirit Miguta" : ["St. John Paul II Kianyogu","Holy Family Giathieko","St. Teresa Mitahato","St. Joseph the Worker Raiyaini","St. Monica Raini"], 
            "St. Teresa of the Child Jesus Ngenya" : ["St. Patrick’s Nyanduma","St. Francis Kaguongo","St. Veronica Njagu","St. Mary of Holy Rosary Kariguini","Mary Immaculate Karatina","St. Mary Mbariki","St. Kizito Mburiri","St. John Evangelist Gachoire"],
            "St. John the Evangelist Githiga" : ["St. Joseph the Worker Gatitu","Mary Mother of God Matuguta","St. Peter the Rock Gathiong’oi"]
        },
    }
    db = SessionLocal()
    try:
        print("Starting database seeding...")
        
        # Correctly loop through the Deaneries (key) and their Parishes (a dictionary)
        for deanery_name, parishes_dict in seed_data.items():
            
            # --- 1. Handle the Deanery ---
            deanery_obj = db.query(Deanery).filter_by(name=deanery_name.strip()).first()
            if not deanery_obj:
                deanery_obj = Deanery(name=deanery_name.strip())
                db.add(deanery_obj)
                # We use flush to get the deanery_obj.id before the final commit
                db.flush()
                print(f"Created Deanery: {deanery_name}")

            # Correctly loop through the Parishes (key) and their Outstations (a list)
            for parish_name, outstations_list in parishes_dict.items():
                
                # --- 2. Handle the Parish ---
                # Check for existing parish within the *same deanery* to be safe
                parish_obj = db.query(Parish).filter_by(name=parish_name.strip(), deanery_id=deanery_obj.id).first()
                if not parish_obj:
                    parish_obj = Parish(name=parish_name.strip(), deanery_id=deanery_obj.id)
                    db.add(parish_obj)
                    # Flush to get the parish_obj.id for the outstations
                    db.flush()
                    print(f"  - Created Parish: {parish_name}")
                
                # --- 3. Handle the Outstations ---
                # Correctly loop through the list of outstation names
                for outstation_name in outstations_list:
                    outstation_obj = db.query(Outstation).filter_by(name=outstation_name.strip(), parish_id=parish_obj.id).first()
                    if not outstation_obj:
                        outstation = Outstation(name=outstation_name.strip(), parish_id=parish_obj.id)
                        db.add(outstation)
                        print(f"    - Created Outstation: {outstation_name}")

        # Commit the entire transaction once all objects have been added
        db.commit()
        print("\nSeeding completed successfully! All data has been committed.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Rolling back changes.")
        db.rollback()  # Roll back the transaction on error
    finally:
        db.close()     # Ensure the session is closed
        print("Database session closed.")


# To run the seeding script
if __name__ == "__main__":
    seed_data()