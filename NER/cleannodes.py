import pandas as pd
import re
from collections import defaultdict

def canonicalize_entity(entity):
    """
    Canonicalize entity names to merge variants under single canonical forms
    """
    entity_clean = str(entity).strip()
    entity_norm = entity_clean.lower()
    
    # Remove extra whitespace and punctuation for matching
    entity_norm = re.sub(r'\s+', ' ', entity_norm)
    entity_norm = re.sub(r'[().,;:!?\"\']', '', entity_norm)
    entity_norm = entity_norm.strip()
    
    # RDIF variants - all map to "РФПИ"
    rdif_patterns = [
        r'^рфпи$',
        r'^российского фонда прямых инвестиций$',
        r'^российский фонд прямых инвестиций$',
        r'^российского фонда прямых инвестиций рфпи$',
        r'^российский фонд прямых инвестиций рфпи$',
        r'^russian direct investment fund$',
        r'^rdif$'
    ]
    
    for pattern in rdif_patterns:
        if re.match(pattern, entity_norm):
            return 'РФПИ'
    
    # Putin variants - all map to "Владимир Путин"
    putin_patterns = [
        r'^владимир путин$',
        r'^владимира путина$',
        r'^путин$',
        r'^путина$',
        r'^в путин$',
        r'^владимир владимирович путин$'
    ]
    
    for pattern in putin_patterns:
        if re.match(pattern, entity_norm):
            return 'Владимир Путин'
    
    # Dmitriev variants - all map to "Кирилл Дмитриев"
    dmitriev_patterns = [
        r'^кирилл дмитриев$',
        r'^кирилла дмитриева$',
        r'^дмитриева$',
        r'^к дмитриев$',
        r'^кирилл александрович дмитриев$'
    ]
    
    for pattern in dmitriev_patterns:
        if re.match(pattern, entity_norm):
            return 'Кирилл Дмитриев'
    
    # Trump variants - all map to "Дональд Трамп"
    trump_patterns = [
        r'^дональд трамп$',
        r'^дональда трампа$',
        r'^трамп$',
        r'^трампа$',
        r'^д трамп$',
        r'^donald trump$'
    ]
    
    for pattern in trump_patterns:
        if re.match(pattern, entity_norm):
            return 'Дональд Трамп'
    
    # News agencies canonicalization
    if entity_norm in ['тасс', 'итар-тасс']:
        return 'ТАСС'
    
    if entity_norm in ['прайм', 'prime']:
        return 'ПРАЙМ'
    
    if entity_norm in ['смиа', 'сми']:
        return 'СМИ'
    
    # Return original entity if no canonicalization needed
    return entity_clean

def clean_and_normalize_ner_dataset(input_file, output_file, min_occurrences=5):
    """
    Main function to clean, normalize, and deduplicate NER dataset
    """
    print("Loading dataset...")
    df = pd.read_csv(input_file)
    print(f"Initial dataset size: {len(df):,} rows")
    print(f"Initial columns: {df.columns.tolist()}")
    print(f"Unique entities before cleaning: {df['Entity'].nunique():,}")
    
    # 1. Apply entity canonicalization
    print("\nCanonicalizing entity names...")
    df['Entity_canonical'] = df['Entity'].apply(canonicalize_entity)
    
    # 2. EXPANDED BLACKLIST - Remove generic/non-analytical entities
    BLACKLIST = {
        # Countries and major geopolitical entities
        'россия', 'россии', 'россию', 'россией', 'российская федерация', 'рф',
        'украина', 'украины', 'украину', 'украиной', 'украине',
        'москва', 'москве', 'москвы', 'москву', 'москвой',
        'китай', 'китае', 'китая', 'китаю', 'китаем', 'кнр',
        'сша', 'америка', 'американский', 'американская', 'американские',
        'европа', 'евросоюз', 'европейский', 'европейская', 'европейские',
        'саудовская аравия', 'саудовской аравии', 'саудовскую аравию',
        
        # Government institutions and generic terms
        'правительство', 'правительства', 'правительству', 'правительством',
        'президент', 'президента', 'президенту', 'президентом',
        'министерство', 'министерства', 'министерству', 'министерством',
        'минздрав', 'мид', 'минфин', 'минэкономразвития',
        'кремль', 'кремля', 'кремлю', 'кремлем',
        'вашингтон', 'вашингтона', 'вашингтону', 'вашингтоном',
        'госдума', 'совет федерации', 'парламент',
        
        # News agencies and media
        'тасс', 'итар-тасс', 'прайм', 'сми', 'смиа',
        'риа новости', 'рбк', 'коммерсантъ', 'ведомости',
        'интерфакс', 'россия сегодня', 'rt', 'russia today',
        'bbc', 'cnn', 'reuters', 'bloomberg', 'ap', 'afp',
        'dw', 'france24', 'euronews',
        
        # Generic organizational terms
        'агентство', 'служба', 'комитет', 'департамент',
        'управление', 'администрация', 'ведомство',
        'корпорация', 'холдинг', 'группа компаний',
        
        # Generic locations
        'центр', 'регион', 'область', 'край', 'республика',
        'город', 'район', 'улица', 'площадь',
        
        # Generic financial/economic terms
        'банк', 'банка', 'банку', 'банком',
        'биржа', 'биржи', 'бирже', 'биржей',
        'рынок', 'рынка', 'рынку', 'рынком',
        'экономика', 'экономики', 'экономике', 'экономикой',
        
        # Generic titles and positions
        'директор', 'директора', 'директору', 'директором',
        'руководитель', 'руководителя', 'руководителю', 'руководителем',
        'председатель', 'председателя', 'председателю', 'председателем',
        'заместитель', 'заместителя', 'заместителю', 'заместителем',
        'министр', 'министра', 'министру', 'министром',
        'губернатор', 'губернатора', 'губернатору', 'губернатором',
        'мэр', 'мэра', 'мэру', 'мэром',
        
        # Generic company/organization suffixes
        'ооо', 'зао', 'оао', 'ао', 'пао', 'нко',
        'ltd', 'llc', 'inc', 'corp', 'gmbh',
        
        # Other generic terms
        'компания', 'компании', 'компанию', 'компанией',
        'организация', 'организации', 'организацию', 'организацией',
        'учреждение', 'учреждения', 'учреждению', 'учреждением',
        'фирма', 'фирмы', 'фирму', 'фирмой',
        'предприятие', 'предприятия', 'предприятию', 'предприятием'
    }
    
    # 3. Remove blacklisted entities
    print("Removing blacklisted entities...")
    initial_count = len(df)
    df = df[~df['Entity_canonical'].str.lower().isin(BLACKLIST)]
    print(f"Removed {initial_count - len(df):,} blacklisted entity mentions")
    
    # 4. Count occurrences per canonical entity (unique articles)
    print("Calculating entity occurrences...")
    entity_article_counts = df.groupby(['Entity_canonical', 'Entity_Type'])['Article_ID'].nunique().reset_index()
    entity_article_counts = entity_article_counts.rename(columns={'Article_ID': 'New_Occurrences'})
    
    print(f"Entity counts columns: {entity_article_counts.columns.tolist()}")
    print(f"Entity counts shape: {entity_article_counts.shape}")
    
    # 5. Filter entities with minimum occurrences
    entities_to_keep = entity_article_counts[entity_article_counts['New_Occurrences'] >= min_occurrences]
    print(f"Entities with >= {min_occurrences} occurrences: {len(entities_to_keep):,}")
    
    # Create set for faster lookup
    keep_entities = set(zip(entities_to_keep['Entity_canonical'], entities_to_keep['Entity_Type']))
    
    # 6. Filter main dataset
    df_filtered = df[df[['Entity_canonical', 'Entity_Type']].apply(tuple, axis=1).isin(keep_entities)].copy()
    print(f"Filtered dataset columns: {df_filtered.columns.tolist()}")
    
    # 7. Add occurrence counts to main dataset
    df_final = df_filtered.merge(
        entity_article_counts[['Entity_canonical', 'Entity_Type', 'New_Occurrences']], 
        on=['Entity_canonical', 'Entity_Type'], 
        how='left'
    )
    
    print(f"After merge columns: {df_final.columns.tolist()}")
    
    # 8. Handle column renaming properly
    if 'Occurrences' in df_final.columns:
        df_final = df_final.drop(columns=['Occurrences'])
        print("Dropped original 'Occurrences' column to avoid duplication")
    
    # 9. Drop old 'Entity' column BEFORE renaming 'Entity_canonical'
    if 'Entity' in df_final.columns:
        df_final = df_final.drop(columns=['Entity'])
        print("Dropped original 'Entity' column")
    
    # 10. Rename columns
    df_final = df_final.rename(columns={
        'Entity_canonical': 'Entity',
        'New_Occurrences': 'Occurrences'
    })
    
    # 11. Check what columns we actually have before reordering
    available_columns = df_final.columns.tolist()
    print(f"Available columns before reordering: {available_columns}")
    
    # 12. Reorder columns
    desired_columns = ['Article_ID', 'Date', 'Source', 'Entity', 'Entity_Type', 'Occurrences', 'Context_Text']
    columns_order = [col for col in desired_columns if col in available_columns]
    
    # Add any remaining columns that weren't in our desired list
    for col in available_columns:
        if col not in columns_order:
            columns_order.append(col)
    
    print(f"Final column order: {columns_order}")
    df_final = df_final[columns_order]
    
    # 13. Verify no duplicate column names
    if len(df_final.columns) != len(set(df_final.columns)):
        print("WARNING: Duplicate column names detected!")
        print(f"Columns: {df_final.columns.tolist()}")
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]
        print(f"After removing duplicates: {df_final.columns.tolist()}")
    
    # 14. Sort by occurrences and entity name
    if 'Occurrences' in df_final.columns and 'Entity' in df_final.columns:
        df_final = df_final.sort_values(['Occurrences', 'Entity'], ascending=[False, True])
        print("Sorted by Occurrences and Entity")
    elif 'Occurrences' in df_final.columns:
        df_final = df_final.sort_values('Occurrences', ascending=False)
        print("Sorted by Occurrences only")
    
    df_final = df_final.reset_index(drop=True)
    
    # 15. Save cleaned dataset
    df_final.to_csv(output_file, index=False)
    
    # 16. Print summary statistics
    print(f"\n=== FINAL CLEANING SUMMARY ===")
    print(f"Original dataset: {len(df):,} rows")
    print(f"Final dataset: {len(df_final):,} rows")
    print(f"Reduction: {((len(df) - len(df_final)) / len(df) * 100):.1f}%")
    print(f"Unique entities before: {df['Entity_canonical'].nunique():,}")
    print(f"Unique entities after: {df_final['Entity'].nunique():,}")
    
    print(f"\nEntity type distribution:")
    print(df_final['Entity_Type'].value_counts())
    
    if 'Occurrences' in df_final.columns:
        print(f"\nTop 20 most frequent entities:")
        top_entities = df_final.groupby('Entity')['Occurrences'].first().sort_values(ascending=False).head(20)
        for entity, count in top_entities.items():
            print(f"{entity}: {count:,}")
    
    # 17. Show what was removed
    print(f"\n=== BLACKLISTED ENTITIES REMOVED ===")
    print("Examples of removed entity types:")
    print("- News agencies: ТАСС, ПРАЙМ, СМИ")
    print("- Government institutions: Минздрав, МИД")
    print("- Generic locations: Countries, cities")
    print("- Generic organizational terms")
    
    print(f"\nFinal dataset saved to: {output_file}")
    return df_final

# Run the cleaning process
if __name__ == "__main__":
    cleaned_df = clean_and_normalize_ner_dataset(
        input_file='ner_entity_dataset_cleaned.csv',
        output_file='ner_entity_dataset_final_refined.csv',
        min_occurrences=5
    )
    
    print("\n=== VERIFICATION ===")
    print("Checking for RDIF variants in final dataset:")
    if len(cleaned_df) > 0:
        rdif_variants = cleaned_df[cleaned_df['Entity'].str.contains('РФПИ|фонд|RDIF', case=False, na=False)]['Entity'].unique()
        print(f"Found {len(rdif_variants)} fund-related entities")
        
        # Show top 10 fund entities
        fund_entities = cleaned_df[cleaned_df['Entity'].str.contains('РФПИ|фонд|RDIF', case=False, na=False)]
        top_funds = fund_entities.groupby('Entity')['Occurrences'].first().sort_values(ascending=False).head(10)
        print("\nTop 10 fund-related entities:")
        for entity, count in top_funds.items():
            print(f"  {entity}: {count:,} occurrences")
