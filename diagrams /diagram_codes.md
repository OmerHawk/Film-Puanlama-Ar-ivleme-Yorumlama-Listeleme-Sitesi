# Use Case Diagram

``` 
@startuml
left to right direction
skinparam packageStyle rectangle
skinparam usecase {
    BackgroundColor LightCyan
    BorderColor DarkCyan
}

actor "Ziyaretçi" as Guest
actor "Kayıtlı Kullanıcı" as User
actor "Admin" as Admin

Guest <|-- User : "Kalıtım\n(Kullanıcı, ziyaretçinin her yaptığını yapar)"

rectangle "Film Arşivleme ve Puanlama Platformu" {

  package "Kullanıcı İşlemleri" {
    usecase "Kayıt Ol" as UC_Register
    usecase "Giriş Yap" as UC_Login
    usecase "Şifremi Unuttum" as UC_Forgot
    usecase "Profili Görüntüle/Düzenle" as UC_Profile
    usecase "Çıkış Yap" as UC_Logout
  }

  package "Film ve Keşif İşlemleri" {
    usecase "Film Ara" as UC_Search
    usecase "Detaylı Filtreleme Yap" as UC_Filter
    usecase "Film Detaylarını İncele" as UC_MovieDetails
    usecase "Film Önerilerini Gör" as UC_Recs
  }

  package "Etkileşim ve Arşivleme" {
    usecase "Filmi Puanla" as UC_Rate
    usecase "Filme Yorum Yap" as UC_Review
    usecase "Kendi Yorumunu Yönet (Düzenle/Sil)" as UC_ManageReview
    usecase "Diğer Yorumları Oku" as UC_ReadReviews
    usecase "İzleme Listelerini Görüntüle" as UC_ViewLists
    usecase "Listeye Film Ekle/Çıkar" as UC_ManageList
    usecase "Kişisel İstatistikleri Gör" as UC_Stats
  }

  package "Yönetici İşlemleri" {
    usecase "Admin Paneline Eriş" as UC_AdminDash
    usecase "Kullanıcıları Yönet" as UC_ManageUsers
    usecase "Hesabı Askıya Al/Engelle" as UC_Suspend
    usecase "Yorumları Modere Et" as UC_Moderate
    usecase "Uygunsuz Yorumu Sil" as UC_DeleteReview
    usecase "Sistem Loglarını İncele" as UC_Logs
  }
}

' Ziyaretçi Bağlantıları
Guest --> UC_Register
Guest --> UC_Login
Guest --> UC_Forgot
Guest --> UC_Search
Guest --> UC_MovieDetails
Guest --> UC_ReadReviews

' Kayıtlı Kullanıcı Bağlantıları (Ziyaretçiden miras alır)
User --> UC_Profile
User --> UC_Logout
User --> UC_Recs
User --> UC_Rate
User --> UC_Review
User --> UC_ManageReview
User --> UC_ViewLists
User --> UC_ManageList
User --> UC_Stats

' Admin Bağlantıları
Admin --> UC_Login
Admin --> UC_AdminDash
Admin --> UC_ManageUsers
Admin --> UC_Moderate
Admin --> UC_Logs

' Include (Dahil Etme) ve Extend (Genişletme) İlişkileri
UC_Search <.. UC_Filter : <<extend>>
UC_Rate ..> UC_Login : <<include>>
UC_Review ..> UC_Login : <<include>>
UC_ManageList ..> UC_Login : <<include>>
UC_Profile ..> UC_Login : <<include>>

UC_ManageUsers <.. UC_Suspend : <<extend>>
UC_Moderate <.. UC_DeleteReview : <<extend>>

@enduml
```

# Class Diagram

```
@startuml
skinparam classAttributeIconSize 0
skinparam class {
    BackgroundColor AliceBlue
    BorderColor DarkBlue
}

class User {
  - userId: int
  - username: String
  - passwordHash: String
  + login(): boolean
  + logout(): void
}

class RegisteredUser {
  + submitRating(movieId: int, ratingScore: int): void
  + addReview(movieId: int, text: String): void
  + manageWatchlist(movieId: int): void
}

class SystemAdmin {
  + banUser(userId: int): void
  + deleteReview(reviewId: int): void
}

class Movie {
  - movieId: int
  - title: String
  - releaseDate: Date
  - averageRating: float
  + getDetails(): String
  + updateAverageRating(): void
}

class Rating {
  - ratingId: int
  - ratingScore: int
  - ratingDate: Date
  + saveRating(): void
}

class Review {
  - reviewId: int
  - text: String
  - reviewDate: Date
  - status: String
  + saveReview(): void
}

class Genre {
  - genreId: int
  - genreName: String
  + getMoviesByGenre(): List<Movie>
}

class Watchlist {
  - dateAdded: Date
  + getList(): List<Movie>
}

' Kalıtım (Inheritance) İlişkileri
User <|-- RegisteredUser
User <|-- SystemAdmin

' İlişkilendirme ve Çokluk (Multiplicity) Değerleri
RegisteredUser "1" -- "0..*" Rating : gives >
RegisteredUser "1" -- "0..*" Review : writes >
RegisteredUser "1" -- "1" Watchlist : has >

Movie "1" -- "0..*" Rating : receives <
Movie "1" -- "0..*" Review : has <
Movie "1..*" -- "1..*" Genre : belongs to >
Watchlist "0..*" -- "0..*" Movie : contains >

SystemAdmin "1" ..> "0..*" User : manages
SystemAdmin "1" ..> "0..*" Review : moderates

@enduml
```

# State Diagrams

## Review Object

```
@startuml
skinparam state {
  BackgroundColor LightCyan
  BorderColor DarkCyan
}
hide empty description

[*] --> Draft : Yorum yazılmaya başlandı
Draft --> PendingApproval : Gönderildi
PendingApproval --> Published : Admin onayladı
Published --> Suspended : Şikayet edildi
Suspended --> Published : İhlal bulunmadı (Geri yüklendi)
Suspended --> Deleted : Uygunsuz bulundu
Published --> Deleted : Kullanıcı/Admin sildi
Deleted --> [*]
@enduml
```

## User Account Object

```
@startuml
skinparam state {
  BackgroundColor LightYellow
  BorderColor GoldenRod
}
hide empty description

[*] --> Unverified : Kayıt formu dolduruldu
Unverified --> Active : E-posta doğrulandı
Active --> Suspended : Kural ihlali (Geçici engel)
Suspended --> Active : Ceza süresi doldu
Suspended --> Banned : Tekrarlayan ihlal (Kalıcı engel)
Active --> Banned : Ağır kural ihlali
Active --> Deleted : Kullanıcı hesabını sildi
Banned --> [*]
Deleted --> [*]
@enduml
```

## Watchlist Item Object

```
@startuml
skinparam state {
  BackgroundColor Honeydew
  BorderColor Green
}
hide empty description

[*] --> PlanToWatch : "İzlenecekler"e eklendi
PlanToWatch --> Watched : İzlenildi olarak işaretlendi
Watched --> PlanToWatch : Yanlış işaretleme geri alındı
PlanToWatch --> Removed : Listeden çıkarıldı
Watched --> Removed : Listeden çıkarıldı
Removed --> [*]
@enduml
```

## Report Object

```
@startuml
skinparam state {
  BackgroundColor MistyRose
  BorderColor FireBrick
}
hide empty description

[*] --> Submitted : Kullanıcı şikayet oluşturdu
Submitted --> InReview : Admin incelemeye aldı
InReview --> ActionTaken : İhlal tespit edildi (İşlem yapıldı)
InReview --> Dismissed : İhlal bulunmadı (Reddedildi)
ActionTaken --> [*]
Dismissed --> [*]
@enduml
```

# Activity Diagrams

## Movie Rating Workflow

```
@startuml
skinparam activity {
  BackgroundColor LightCyan
  BorderColor DarkCyan
}

start
:Film Detay Sayfasına Gir;
if (Kullanıcı Giriş Yapmış mı?) then (Hayır)
  :Giriş Sayfasına Yönlendir;
  stop
else (Evet)
  :1-10 Arası Puan Seç ve Gönder;
  :Veritabanında Kontrol Et;
  if (Kullanıcı bu filme daha önce puan vermiş mi?) then (Evet)
    :Eski Puanı Yeni Puanla Güncelle;
  else (Hayır)
    :Veritabanına Yeni "Rating" Kaydı Ekle;
  endif
  :Filmin Genel Ortalama Puanını Yeniden Hesapla;
  :Arayüzde Güncel Ortalamayı Göster;
  stop
endif
@enduml
```

## Login and Role Orientation Workflow

```
@startuml
skinparam activity {
  BackgroundColor LightYellow
  BorderColor GoldenRod
}

start
:E-posta ve Şifre Gir;
:Veritabanında Kimlik Doğrulaması Yap;
if (Bilgiler Doğru mu?) then (Hayır)
  :Arayüzde "Hatalı Giriş" Mesajı Göster;
  stop
else (Evet)
  :Kullanıcının Rolünü (Yetkisini) Kontrol Et;
  if (Rol Nedir?) then (System Admin)
    :Admin Dashboard'a Yönlendir;
  else (Registered User)
    :Kullanıcı Ana Sayfasına Yönlendir;
  endif
  stop
endif
@enduml
```

## Comment Moderation Flow

```
@startuml
skinparam activity {
  BackgroundColor MistyRose
  BorderColor FireBrick
}

start
:Şikayet Edilen Yorumları Listele;
:İncelenecek Yorumu Seç ve Oku;
if (Yorum Platform Kurallarına Aykırı mı?) then (Evet)
  :Yorumu Veritabanından Sil / Gizle;
  :Yorum Sahibine Uyarı Bildirimi Gönder;
else (Hayır)
  :Şikayeti Reddet (Yorum Yayında Kalır);
endif
:Yapılan İşlemi Sistem Loglarına Kaydet;
stop
@enduml
```

# Sequence Diagrams

## Rating a Movie

```
@startuml
skinparam sequence {
    ParticipantBackgroundColor AliceBlue
    ParticipantBorderColor DarkBlue
    LifeLineBorderColor DarkBlue
}

actor "Kayıtlı Kullanıcı\n(RegisteredUser)" as RU
boundary "MoviePlatform_UI" as UI
control "Movie_Controller" as Ctrl
entity "Rating" as R
entity "Movie" as M

RU -> UI : submitRating(movieId, ratingScore)
activate UI

UI -> Ctrl : validateRating(ratingScore)
activate Ctrl

Ctrl -> R : saveRating()
activate R
R --> Ctrl : success
deactivate R

Ctrl -> M : updateAverageRating()
activate M
M --> Ctrl : updated
deactivate M

Ctrl --> UI : ratingResponse(successMessage)
deactivate Ctrl

UI --> RU : "Puan başarıyla kaydedildi"
deactivate UI
@enduml
```

## Entering the System

```
@startuml
skinparam sequence {
    ParticipantBackgroundColor LightYellow
    ParticipantBorderColor GoldenRod
    LifeLineBorderColor GoldenRod
}

actor "Ziyaretçi\n(Guest)" as G
boundary "Login_UI" as UI
control "Auth_Controller" as Auth
entity "User" as U

G -> UI : e-posta ve şifre girer
activate UI

UI -> Auth : login()
activate Auth

Auth -> U : verifyCredentials(email, passwordHash)
activate U
U --> Auth : role (RegisteredUser / SystemAdmin)
deactivate U

Auth --> UI : authSuccess(token)
deactivate Auth

UI --> G : Ana sayfaya (Dashboard) yönlendir
deactivate UI
@enduml
```

## Deleting Inappropiete Comments

```
@startuml
skinparam sequence {
    ParticipantBackgroundColor MistyRose
    ParticipantBorderColor FireBrick
    LifeLineBorderColor FireBrick
}

actor "Sistem Yöneticisi\n(SystemAdmin)" as Admin
boundary "AdminPanel_UI" as UI
control "Moderation_Controller" as Ctrl
entity "Review" as R

Admin -> UI : deleteReview(reviewId)
activate UI

UI -> Ctrl : processDeletion(reviewId)
activate Ctrl

Ctrl -> R : status = "Deleted"
activate R
R -> R : saveReview()
R --> Ctrl : success
deactivate R

Ctrl --> UI : deletionConfirmed
deactivate Ctrl

UI --> Admin : "Yorum kalıcı olarak silindi"
deactivate UI
@enduml
```
