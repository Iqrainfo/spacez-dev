PGDMP                       |            spacez    16.3    16.3     �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    41017    spacez    DATABASE     y   CREATE DATABASE spacez WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_India.1252';
    DROP DATABASE spacez;
                postgres    false            �          0    49228    transactions 
   TABLE DATA           �   COPY public.transactions (transaction_id, transaction_type, order_type, amount, coin_code, price, quantity, payment_method, fee_amount, fee_currency, transaction_status, created_at, updated_at, user_id, clr_balance) FROM stdin;
    public          postgres    false    217   $       �          0    49243    user_balance 
   TABLE DATA           �   COPY public.user_balance (id, balance, status, payment_method, order_type, order_amount, clr_balance, updated_at, user_id) FROM stdin;
    public          postgres    false    218   =       �          0    41019    users 
   TABLE DATA           �   COPY public.users (username, email, password_hash, mobile_number, identity_card_no, issuing_authority, kyc_done, id_created_on, created_at, updated_at, last_login, last_profile_chnaged_at, "Address", user_id) FROM stdin;
    public          postgres    false    216   >	       �   	  x����jQF�3O�pP�^u�]�	��S�I���i����g��Ê�%
��=���������i����\>���pA����n��/׷��Ѐ�Ĵ
�j�"��Tp륀�`��%p�}qIiT���3E�� ow�����V�������{N�G�H�R�@$i@rP�@Bg3�����*D+��"Pʈ�{S,6������tb^�W�=�$�G��knE���@���E�M�fg&���t�	�l�G�q��2�����      �   �   x���1N1��z�{�lǎ���9�6q�����gX�@���|�K/�G�C!�9!5sӺ����~����������v�����Ѐ�´�j�"�������d�<
8�8�N�J���Q�cN�x" �Tʣu)���7�Z�"��q�
Hр&�(���f�JL.��� ��M���������@��;ʅ�^ʮ���߅�ڛ�y�W�3�(������d�6�q��u� J*�1      �   k  x���KK�@�ד_�Ev:qΜ��L�`��ׯZ�Ԉ�ɵ�M�Mz��-�"/���9����U���pZֶZ�iSϮ�fɫ����xu?��㮏ǯ}�p�PA�I�z|y�F�u=��:?zHGWq6�Mz.�I���>N'�{x�|,�cu?�#��1y`4C �Q�@郓�fӹM�^.�ʒ�p�e�|�.����>S�%�	���:�et�P	d��*Pjh*�0��J)��Vղ$�6_��;[�.� �NR�<i���-����v]��#oFOqlO����;�qB��1��Σ�|����qÇ�#�����3�|��k)��D��eEf-U"�T$R͒l_S�1O$8/��8��`�<     