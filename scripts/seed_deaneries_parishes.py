from config.db import SessionLocal
# Explicitly import all models to register relationships
import models.deanery
import models.parish
import models.user
import models.outstation

from models.deanery import Deanery
from models.parish import Parish
from models.outstation import Outstation
# Map of deanery to list of parishes
def seed_data():
    deaneries_data = {
        "MANGU DEANERY": [
            "St. Teresa Gachege", "St. Anne Mataara", "St. Peter Nyamangara", "St. John the Baptist Mangu",
            "Our Lady of Fatima Kiriko", "St. Teresa Kianguno", "St. Stephen Kairi", "Our Lady of the Holy Rosary Kamwangi"
        ],
        "GATUNDU DEANERY": [
            "Our Lady of Annunciation Gatitu", "Matyrs of Uganda Gatundu", "CTK Karinga", "St. Joseph Kiganjo",
            "Archangel Gabriel Mutomo", "St. John the Baptist Munyu-ini", "St. Stephen Ituru", "St. Joseph Mutunguru",
            "Mary Help of Christians Ndundu"
        ],
        "THIKA DEANERY": [
            "St. Patrick's Thika", "St. Bernadette Ngoigwa", "St. Mathias Mulumba Makongeni", "St. Maria Magdalena Munyu",
            "St. Achilles Kiwanuka", "Holy Rosary Witeithie", "Immaculate Conception Kilimambogo"
        ],
        "RUIRU DEANERY": [
            "St. Teresa Kalimoni", "St. Francis of Assisi Ruiru", "St. Christopher Kimbo", "Presentation of the Lord Juja Farm",
            "St. Peter Kwihota", "St. Augustine Juja", "Mary Immaculate Kumura", "Divine Mercy Kalimoni", "St. Paul Mugutha"
        ],
        "MAKADARA DEANERY": [
            "Holy Trinity Buruburu", "St. Teresa Eastleigh", "St. Joseph Jericho", "St. Joseph & Mary Shauri Moyo",
            "Our Lady of Visitation Makadara", "St. Mary Mukuru", "St. Mary Magdalene Kariokor", "Blessed Sacrament Buruburu"
        ],
        "WESTERN DEANERY": [
            "Sacred Heart Dagoretti", "Regina Caeli Karen", "CTK Kibera", "Our Lady of Guadalupe",
            "St. John Langata", "St. Michael Otiende", "Mary Queen of Apostles Dagoreti"
        ],
        "CENTRAL DEANERY": [
            "Holy Family Basilica", "St. Francis Xavier Parklands", "St. Paul Chaplaincy", "St. Peter Clavers",
            "Donbosco Upperhill", "Our Lady Queen of Peace South B", "St. Catherines of Alexandria South C"
        ],
        "KABETE DEANERY": [
            "St. Raphael Kabete", "St. Joseph Kangemi", "St. Catherine Sienna", "Holy Rosary Ridgeways",
            "Consolata Shrine", "Holy Trinity Kileleshwa", "St Austin Msongari"
        ],
        "KIAMBU DEANERY": [
            "St. Stephen Gahie", "St. Joseph Gathanga", "Holy Rosasry Ikinu", "St. Martin de Porres Karuri",
            "St. Peter & Paul Kiambu", "Our Lady of Victories Lioki", "All Saints Riara", "Our Lady of Rosary Ting'ang'a"
        ],
        "LIMURU DEANERY": [
            "Our Lady of Mt. Carmel Ngarariga", "St. Joseph the Worker Kereita", "St. Charles Lwanga Kamirithu Parish",
            "St. Joseph Loreto", "St. Andrews Rironi", "St. Charles Lwanga Githirioni", "St. Francis of Assisi Limuru"
        ],
        "KIKUYU DEANERY": [
            "Immaculate Conception Gicharani", "Holy Eacharist King'eero", "St. John the Baptist Riruta",
            "Our Lady of the Holy Rosary Ruku", "St. Charles Lwanga Waithaka", "St. Peter the Apostle Kikuyu",
            "St. Joseph Kerwa", "St. Joseph the Worker Muguga", "Holy Cross Thigio", "St. Peter the Rock Kinoo"
        ],
        "GITHUNGURI DEANERY": [
            "Holy Family Githunguri", "Nativity of our Lord Kagwe", "Our Lady of Assumption Kambaa",
            "All Saints Komothai", "Holy Spirit Miguta", "St. Teresa of the Child Jesus Ngenya",
            "St. John the Evangelist Githiga"
        ],
        "EASTERN DEANERY": [
            "CTK Embakasi", "St. Monica Njiru", "St. Joseph Freinadimetz Ruai", "St. Peter Ruai",
            "St. Anne & Joachim Soweto", "St. Vincent de Paul Kamulu", "Mary Immaculate Mihango",
            "Holy Family Utawala", "Divine Word, Kayole", "St. Daniel Comboni", "St. Arnold Janssen Komarock"
        ],
        "OUTERING DEANERY": [
            "St. Jude Donholm", "Holy Innocents Tassia", "Holy Trinity Kariobangi North",
            "Divine Mercy Kariobangi South", "St. Andre Bassette Dandora", "Assumption of Mary Umoja",
            "Holy Cross Dandora"
        ],
        "RUARAKA DEANERY": [
            "St. Dominic Savio, Mwiki", "St. Benedicts Survey", "St. Claire Kasarani",
            "Madre Teresa of Calcutta, Zimmerman", "Sacred Heart Babadogo", "Queen of Apostles Ruaraka"
        ],
        "GITHURAI DEANERY": [
            "St. Joseph Mukasa Kahawa West", "St. Francis of Assisi Mwihoko", "St. Joseph the Worker Kahawa Sukari",
            "Our Lady Consolata Kahawa Farmers", "CTK Kimbo", "St. Lucia Membley", "Holy Mary Mother of God Githurai"
        ]
    }

    db = SessionLocal()

    for deanery_name, parish_list, in deaneries_data.items():
        # Create or fetch deanery
        deanery = db.query(Deanery).filter_by(name=deanery_name).first()
        if not deanery:
            deanery = Deanery(name=deanery_name)
            db.add(deanery)
            db.commit()
            db.refresh(deanery)

        # Add parishes
        for parish_name in parish_list:
            existing = db.query(Parish).filter_by(name=parish_name).first()
            if not existing:
                parish = Parish(name=parish_name, deanery_id=deanery.id,deanery_name=deanery_name)
                db.add(parish)

                for outstation_name in [f"{parish_name}"]:
                    outstation = Outstation(name = outstation_name, parish_id = parish.id)
                    db.add(outstation)


    db.commit()
    db.close()

    print("Deaneries and parishes added successfully.")
