import instance from "@/middlewares";


export default {
  name: "events",
  state: () => ({
    data: null,

  }),
  mutations: {
    setData(state, data) {
      state.data = data;
    },

  },
  actions: {
    //     # # event create schema
    // # class EventCreate(BaseModel):
    // #     event_name: str
    // #     event_date: str
    // #     img_url: str

    // # # event update schema
    // # class EventUpdate(BaseModel):
    // #     event_name: str
    // #     event_date: str
    // #     img_url: str
    // #     archived: bool

    // # # event out schema
    // # class EventOut(BaseModel):
    // #     event_id: int
    // #     event_name: str
    // #     event_date: str
    // #     img_url: str
    // #     archived: bool

    // #     model_config = ConfigDict(from_attributes=True)


    // # # function for getting all events
    // # def get_events(db: Session):
    // #     return db.query(Event).order_by(Event.event_id).all()

    // # function for getting unarchived events ASC
    // def get_events(db: Session):
    //     return db.query(Event).filter(Event.archived == False).order_by(Event.event_date).all()

    // # function for getting archived events DESC
    // def get_archived_events(db: Session):
    //     return db.query(Event).filter(Event.archived == True).order_by(Event.event_date.desc()).all()



    // # function for creating a new event
    // def create_event(db: Session, event: EventCreate):
    //     db_event = Event(
    //         event_name=event.event_name,
    //         event_date=event.event_date,
    //         img_url=event.img_url
    //     )
    //     db.add(db_event)
    //     db.commit()
    //     db.refresh(db_event)
    //     return db_event


    // # function for updating an existing event by id
    // def update_event(db: Session, event_id: int, event: EventUpdate):
    //     db_event = db.query(Event).filter(Event.event_id == event_id).first()
    //     db_event.event_name = event.event_name
    //     db_event.event_date = event.event_date
    //     db_event.img_url = event.img_url
    //     db_event.archived = event.archived
    //     db.commit()
    //     db.refresh(db_event)
    //     return db_event


    // # function for deleting an existing event by id
    // def delete_event(db: Session, event_id: int):
    //     event = db.query(Event).filter(Event.event_id == event_id).first()
    //     db.delete(event)
    //     db.commit()
    //     return event
    
    
    // events crud
    // get events
    async getEvents({ commit }) {
        try {
            const response = await instance.get("/api/events");
            if (response) return commit("setData", response.data);
        }
        catch (error) {
            console.log(error);
        }
    },

    // get archived events
    async getArchivedEvents({ commit }) {
        try {
            const response = await instance.get("/api/events/archived");
            if (response) return commit("setData", response.data);
        }
        catch (error) {
            console.log(error);
        }
    },

    // create event
    async createEvent({}, input) {
        try {
            const { event_name, event_date, img_url } = input;
            const response = await instance.post("/api/events", { event_name, event_date, img_url });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // update event
    async updateEvent({}, input) {
        try {
            const { id, event_name, event_date, img_url, archived } = input;
            const response = await instance.put(`/api/events/${id}`, { event_name, event_date, img_url, archived });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // delete event
    async deleteEvent({}, id) {
        try {
            const response = await instance.delete(`/api/events/${id}`);
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    
    
},

namespaced: true,
};