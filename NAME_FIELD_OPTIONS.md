# Name Field Options

The script now supports **flexible name handling** - use either a single `Name` column OR separate `FirstName` and `LastName` columns!

---

## ✅ Option 1: Single Name Column (Traditional)

Your Google Sheet:

| Name | Email | CourseTitle | ... |
|------|-------|-------------|-----|
| John Smith | john@example.com | Python 101 | ... |
| Alice Johnson | alice@example.com | Python 101 | ... |

**What happens:**
- Script uses the `Name` column directly
- No changes needed

---

## ✅ Option 2: Separate First and Last Name Columns (New!)

Your Google Sheet:

| FirstName | LastName | Email | CourseTitle | ... |
|-----------|----------|-------|-------------|-----|
| John | Smith | john@example.com | Python 101 | ... |
| Alice | Johnson | alice@example.com | Python 101 | ... |

**What happens:**
- Script auto-detects `FirstName` and `LastName` columns
- Automatically combines them: `FirstName + " " + LastName`
- Shows: "✓ Detected FirstName and LastName columns - will combine them automatically"
- In emails: "Dear John Smith,"

---

## 📝 Accepted Column Names

### For Full Name:
- `Name` ✅

### For First Name:
- `FirstName` ✅
- `First Name` ✅
- `first_name` ✅
- (case-insensitive)

### For Last Name:
- `LastName` ✅
- `Last Name` ✅
- `last_name` ✅
- (case-insensitive)

---

## 🎬 How It Works

### Scenario 1: Has Single Name Column
```
Sheet columns: Name, Email, CourseTitle, ...

Script behavior:
→ Maps "Name" column
→ Uses it directly
→ Email says: "Dear [Name],"
```

### Scenario 2: Has FirstName + LastName Columns
```
Sheet columns: FirstName, LastName, Email, CourseTitle, ...

Script behavior:
→ Detects both columns automatically
→ Shows: "✓ Detected FirstName and LastName columns"
→ Combines them behind the scenes
→ Email says: "Dear [FirstName LastName],"
```

### Scenario 3: Has Both (Unusual)
```
Sheet columns: Name, FirstName, LastName, Email, ...

Script behavior:
→ Prefers the "Name" column
→ Ignores FirstName/LastName
```

---

## 💡 Examples

### Example 1: Traditional Setup
**Sheet:**
```csv
Name,Email,CourseTitle
John Smith,john@example.com,Python 101
Alice Johnson,alice@example.com,Python 101
```

**Email result:**
```
Dear John Smith,

Congratulations on successfully completing Python 101...
```

### Example 2: Split Names
**Sheet:**
```csv
FirstName,LastName,Email,CourseTitle
John,Smith,john@example.com,Python 101
Alice,Johnson,alice@example.com,Python 101
```

**Email result:**
```
Dear John Smith,

Congratulations on successfully completing Python 101...
```

**Output exactly the same!** ✨

---

## 🔧 Column Mapping Process

### With Single Name:
```
Step 5: Column Mapping
=== Column Mapping for Certificate Delivery ===
Available columns: Name, Email, CourseTitle, ...

[REQUIRED] Map 'Name' (suggested: Name): ← Press Enter
[REQUIRED] Map 'Email' (suggested: Email): ← Press Enter
...
```

### With FirstName + LastName:
```
Step 5: Column Mapping
=== Column Mapping for Certificate Delivery ===
Available columns: FirstName, LastName, Email, CourseTitle, ...

✓ Detected FirstName and LastName columns - will combine them automatically

[REQUIRED] Map 'Email' (suggested: Email): ← Press Enter
...
```

Notice: No prompt for "Name" - it's handled automatically! ✅

---

## ⚠️ Important Notes

### 1. Both First and Last Required
If using split names, you MUST have BOTH:
- ✅ `FirstName` AND `LastName` = Works
- ❌ `FirstName` only = Error (missing Name)
- ❌ `LastName` only = Error (missing Name)

### 2. Empty Values
```csv
FirstName,LastName,Email
John,Smith,john@example.com     ← Works: "Dear John Smith,"
John,,john@example.com          ← Works: "Dear John," (missing last name)
,Smith,john@example.com         ← Works: "Dear Smith," (missing first name)
,,john@example.com              ← SKIPPED: Missing Name
```

### 3. Extra Spaces Handled
```csv
FirstName,LastName
  John  ,  Smith       ← Results in: "John Smith" (spaces trimmed)
```

---

## 🎯 Which Should You Use?

### Use Single `Name` Column When:
- ✅ You already have full names
- ✅ Simple setup
- ✅ Names from existing database

### Use `FirstName` + `LastName` When:
- ✅ You have names split in your system
- ✅ Want to sort by last name
- ✅ Need to personalize with first name only (future feature)
- ✅ Database has separate fields

**Both work perfectly!** Choose what's easiest for your data source.

---

## 🔮 Future Personalization (Coming Soon)

With split names, you could potentially use:
- `{FirstName}` - Just first name ("John")
- `{LastName}` - Just last name ("Smith")
- `{Name}` - Full name ("John Smith")

Currently, all templates use `{Name}` which works with both setups.

---

## 🚀 Quick Start

### If you have split names in your sheet:
1. Just run the script normally: `./run_mailer.sh`
2. When prompted, paste your sheet URL
3. Script auto-detects and says: "✓ Detected FirstName and LastName columns"
4. Everything else works the same!
5. ✨ No special configuration needed!

### If you have a single Name column:
1. Run the script: `./run_mailer.sh`
2. Script maps "Name" column as usual
3. Everything works as before!

---

## 📋 Summary

| Your Sheet Has | Script Does | Email Shows |
|----------------|-------------|-------------|
| `Name` column | Uses it directly | "Dear [Name]," |
| `FirstName` + `LastName` | Auto-combines them | "Dear [FirstName LastName]," |
| Both | Prefers `Name` column | "Dear [Name]," |

**Bottom line:** Use whatever column structure works for your data. The script handles both! 🎉

