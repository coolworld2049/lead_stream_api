import asyncio
import uuid
from datetime import datetime

from dotenv import load_dotenv
from prisma import Prisma

load_dotenv(dotenv_path="../.env")


async def main():
    prisma = Prisma()
    await prisma.connect()

    # Seed Meta
    meta = await prisma.meta.create(
        data={
            'isTest': False,
            'sub1': 'Sub1Value',
            'sub2': 'Sub2Value',
            'sub3': 'Sub3Value',
            'sub4': 'Sub4Value',
            'sub5': 'Sub5Value',
        }
    )

    # Seed Address
    address = await prisma.address.create(
        data={
            'address': '123 Example St',
            'equalToFact': True,
            'country': 'Россия',
            'countryIso': 'RU',
            'postalCode': '123456',
            'region': 'Moscow',
            'regionType': 'OBL',
            'regionFiasId': uuid.uuid4().__str__(),
            'regionKladrCode': '1234567890123',
            'regionArea': 'Moscow Area',
            'regionAreaType': 'OBL',
            'regionAreaFiasId': uuid.uuid4().__str__(),
            'regionAreaKladrCode': '1234567890123',
            'city': 'Moscow',
            'cityType': 'G',
            'cityFiasId': uuid.uuid4().__str__(),
            'cityKladrCode': '1234567890123',
            'settlement': 'Settlement',
            'settlementType': 'S',
            'settlementFiasId': uuid.uuid4().__str__(),
            'settlementKladrCode': '1234567890123',
            'street': 'Example Street',
            'streetType': 'NAB',
            'streetFiasId': uuid.uuid4().__str__(),
            'streetKladrCode': '1234567890123',
            'house': '1',
            'building': 'A',
            'block': 'B',
            'flat': '10',
            'flatType': 'apartment',
        }
    )

    # Seed User
    user = await prisma.user.create(
        data={
            'firstName': 'John',
            'fatherName': 'Middle',
            'lastName': 'Doe',
            'birthDate': datetime(1990, 1, 1),
            'birthPlace': 'City, Country',
            'gender': 'M',
            'phone': '12345678901',
            'email': 'john.doe@example.com',
            'ip': '127.0.0.1',
        }
    )

    # Seed Lead
    lead = await prisma.lead.create(
        data={
            'type': 'lead',
            'apiToken': 'your_api_token',
            'product': 'CREDIT_TRAFFIC',
            'stream': 'stream_identifier',
            'metaId': meta.id,
            'userId': user.id,
            'addressRegId': address.id,
            'addressFactId': address.id,
        }
    )

    # Seed Sale
    await prisma.sale.create(
        data={
            'campaignID': '123e4567-e89b-12d3-a456-426614174000',
            'leadId': lead.id,
        }
    )

    # Seed Consent
    await prisma.consent.create(
        data={
            'status': True,
            'datetime': datetime.now(),
            'userId': user.id,
        }
    )

    # Seed MailingConsent
    await prisma.mailingconsent.create(
        data={
            'status': True,
            'datetime': datetime.now(),
            'userId': user.id,
        }
    )

    # Seed IdentificationCodes
    identification_code = await prisma.identificationcodes.create(
        data={
            'snils': '12345678900',
            'inn': '123456789012',
            "user": {"connect": {"id": user.id}}
        }, include={"user": True}
    )

    # Seed Passport
    await prisma.passport.create(
        data={
            'seria': '1234',
            'number': '567890',
            'issuer': 'Passport Office',
            'issuerCode': '1234',
            'issueDate': datetime(2020, 1, 1),
            'identificationCodes': {
                'connect': {'id': identification_code.id}
            }
        }
    )

    # Close the Prisma connection
    await prisma.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
